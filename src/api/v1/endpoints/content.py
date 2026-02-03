from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException
from api.deps import CurrentUser, get_current_user
from config.dependencies import get_services
from config.products import get_product_by_name
from core.exceptions import ThumbnailGenerationError
from utils.gcs_store import (
    build_gcs_prefix,
    detect_image_ext,
    gcs_url_for,
    detect_video_ext,
)
from infrastructure.clients.veo_client import AdvancedPromptBuilder
from schemas.requests import (
    HookGenerateRequest,
    ThumbnailCompareRequest,
    VideoGenerateRequest,
)
from utils.logger import get_logger

logger = get_logger(__name__)
router = APIRouter()


@router.get("/thumbnail/styles")
async def get_thumbnail_styles():
    services = get_services()
    return {"styles": services.thumbnail_service.get_available_styles()}


@router.post("/hooks/generate")
async def generate_hooks(request: HookGenerateRequest):
    services = get_services()
    product = get_product_by_name(request.product_name)
    if not product:
        raise HTTPException(
            status_code=404, detail=f"Product '{request.product_name}' not found"
        )
    product_dict = (
        product.model_dump() if hasattr(product, "model_dump") else product.__dict__
    )
    hooks = services.hook_service.generate_hooks(
        style=request.style,
        product=product_dict,
        count=request.count,
    )
    return {"hooks": hooks}


@router.post("/thumbnail/compare-styles")
async def generate_thumbnail_compare_styles(
    request: ThumbnailCompareRequest,
    user: CurrentUser,
):
    """같은 훅으로 여러 스타일 썸네일을 한 번에 생성해 비교용으로 반환"""
    services = get_services()
    product = get_product_by_name(request.product_name)
    if not product:
        raise HTTPException(
            status_code=404, detail=f"Product '{request.product_name}' not found"
        )
    product_dict = (
        product.model_dump() if hasattr(product, "model_dump") else product.__dict__
    )

    available = services.thumbnail_service.get_available_styles()
    style_keys = [s["key"] for s in available]
    if request.styles:
        style_keys = [k for k in request.styles if k in style_keys]
    else:
        style_keys = style_keys[: request.max_styles]

    common_hook = (
        request.hook_text or ""
    ).strip() or f"{product_dict.get('name', '제품')} 추천"
    name_by_key = {s["key"]: s["name"] for s in available}
    hook_service = services.hook_service

    results = []
    storage = services.storage_service
    storage.ensure_bucket()
    prefix = build_gcs_prefix(product_dict, "thumbnail")

    hook_psychology_styles = [s["key"] for s in hook_service.get_available_styles()]
    for idx, style_key in enumerate(style_keys):
        if request.auto_hook_per_style:
            hook_style = (
                hook_psychology_styles[idx % len(hook_psychology_styles)]
                if hook_psychology_styles
                else "curiosity"
            )
            hooks = hook_service.generate_hooks(
                style=hook_style,
                product=product_dict,
                count=1,
            )
            hook_text = hooks[0] if hooks else common_hook
        else:
            hook_text = common_hook

        try:
            image = services.thumbnail_service.generate(
                product=product_dict,
                hook_text=hook_text,
                style=style_key,
                include_text_overlay=request.include_text_overlay,
            )
        except ThumbnailGenerationError as e:
            logger.warning(f"스타일 비교: {style_key} 생성 실패, 건너뜀 — {e}")
            continue
        if not image:
            continue
        ext = detect_image_ext(image)
        style_safe = (style_key or "compare").replace(" ", "_")[:20]
        gcs_path = f"{prefix}/compare_{style_safe}_{idx}{ext}"
        storage.upload(
            data=image,
            path=gcs_path,
            content_type="image/png" if ext == ".png" else "image/jpeg",
        )
        url = gcs_url_for(storage, gcs_path)
        results.append(
            {
                "style": style_key,
                "name": name_by_key.get(style_key, style_key),
                "url": url,
                "gcs_path": gcs_path,
                "hook_text": hook_text,
            }
        )

    return {
        "items": results,
        "hook_text": common_hook
        if not request.auto_hook_per_style
        else "(스타일별 자동 생성)",
    }


@router.get("/hooks/styles")
async def get_hook_styles():
    """썸네일/비디오용 훅 전략 9종 (key, name=Key (한글), emoji, description)"""
    return {"styles": get_services().hook_service.get_available_styles()}


@router.get("/video/presets")
async def get_video_presets():
    hook_styles = get_services().hook_service.get_available_styles()
    return {
        "hook_styles": hook_styles,
        "camera_movements": AdvancedPromptBuilder.get_camera_movements(),
        "compositions": AdvancedPromptBuilder.get_compositions(),
        "lighting_moods": AdvancedPromptBuilder.get_lighting_moods(),
        "audio_presets": AdvancedPromptBuilder.get_audio_presets(),
        "durations": [8, 15, 30],
        "resolutions": ["1080p", "720p"],
    }


@router.post("/video/generate")
async def generate_video(request: VideoGenerateRequest, user: CurrentUser):
    services = get_services()
    product = get_product_by_name(request.product_name)
    if not product:
        raise HTTPException(
            status_code=404, detail=f"Product '{request.product_name}' not found"
        )
    product_dict = (
        product.model_dump() if hasattr(product, "model_dump") else product.__dict__
    )

    prompt_builder = AdvancedPromptBuilder()
    prompt_builder.with_product(
        product_dict.get("name", "제품"),
        product_dict.get("description", ""),
        product_dict.get("category", ""),
    )
    prompt_builder.with_marketing_hook(request.hook_text)

    if request.camera_movement:
        prompt_builder.camera_movement = request.camera_movement
    if request.composition:
        prompt_builder.composition = request.composition
    if request.lighting_mood:
        prompt_builder.lighting_mood = request.lighting_mood
    if request.audio_preset:
        prompt_builder.audio_preset = request.audio_preset
    if request.sfx:
        prompt_builder.sfx = request.sfx
    if request.ambient:
        prompt_builder.ambient = request.ambient

    prompt = prompt_builder.build()
    video_result = services.video_service.generate(
        prompt=prompt,
        duration_seconds=request.duration_seconds,
        resolution=request.resolution,
    )

    if isinstance(video_result, bytes):
        storage = services.storage_service
        storage.ensure_bucket()
        prefix = build_gcs_prefix(product_dict, "video")
        ext = detect_video_ext(video_result)
        gcs_path = f"{prefix}/video{ext}"
        storage.upload(
            data=video_result,
            path=gcs_path,
            content_type="video/mp4" if ext == ".mp4" else "application/octet-stream",
        )
        url = gcs_url_for(storage, gcs_path)
        return {"url": url, "gcs_path": gcs_path, "prompt": prompt}

    if isinstance(video_result, str):
        return {"url": video_result, "prompt": prompt}

    raise HTTPException(status_code=500, detail="Video generation failed")
