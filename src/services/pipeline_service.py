"""
파이프라인 서비스
전체 마케팅 파이프라인 오케스트레이션
"""

import asyncio
import random
import time
from datetime import datetime
from collections.abc import Callable
from typing import Optional

from core.exceptions import PipelineError
from core.interfaces import IStorageService
from core.models import (
    CollectedData,
    GeneratedContent,
    PipelineConfig,
    PipelineProgress,
    PipelineResult,
    PipelineStep,
    UploadStatus,
)
from core.prompts import prompt_registry
from core.prompts import marketing_prompts, social_media_prompts  # noqa: F401
from utils.gcs_store import (
    build_gcs_prefix,
    detect_image_ext,
    detect_video_ext,
    gcs_url_for,
)
from utils.logger import (
    get_logger,
    log_error,
    log_info,
    log_section,
    log_step,
    log_success,
    log_timing,
    log_warning,
)
from services.data_collection_service import DataCollectionService
from services.history_service import HistoryService
from services.marketing_service import MarketingService
from services.rag_ingestion_service import RagIngestionService
from services.social_service import SocialMediaService
from services.thumbnail_service import THUMBNAIL_STYLES, ThumbnailService
from services.video_service import VideoService

logger = get_logger(__name__)


class PipelineService:
    """파이프라인 오케스트레이션 서비스"""

    def __init__(
        self,
        data_collection_service: DataCollectionService,
        marketing_service: MarketingService,
        thumbnail_service: ThumbnailService,
        video_service: VideoService,
        storage_service: IStorageService,
        history_service: HistoryService,
        social_media_service: SocialMediaService,
        rag_ingestion_service: RagIngestionService | None = None,
    ) -> None:
        self._collector = data_collection_service
        self._marketing = marketing_service
        self._thumbnail = thumbnail_service
        self._video = video_service
        self._storage = storage_service
        self._history = history_service
        self._social = social_media_service
        self._rag_ingestion = rag_ingestion_service

    async def execute(
        self,
        product: dict,
        config: PipelineConfig,
        progress_callback: Optional[Callable[[PipelineProgress], None]] = None,
    ) -> PipelineResult:
        """파이프라인 실행"""
        log_section(f"파이프라인 실행 시작: {product.get('name', 'N/A')}")
        start_time = time.time()

        progress = PipelineProgress()
        progress.configure_steps(config)
        collected_data = CollectedData()
        generated_content = GeneratedContent()
        strategy: dict = {}
        upload_status = UploadStatus.SKIPPED
        upload_errors: list[str] = []
        upload_enabled = config.upload_to_gcs
        prompt_log: dict[str, dict[str, str]] = {}
        audit_trail: list[dict[str, str]] = [
            {
                "action": "created",
                "by": "system",
                "at": datetime.now().isoformat(),
            }
        ]

        if upload_enabled and not self._storage.health_check():
            log_warning("GCS health check failed - skipping upload.")
            upload_status = UploadStatus.FAILED
            upload_errors.append("GCS health check failed")
            upload_enabled = False

        def record_prompt(name: str) -> None:
            try:
                template = prompt_registry.get(name)
            except KeyError:
                return
            prompt_log[name] = {"version": template.version}

        def update_progress(step: PipelineStep, message: str = "") -> None:
            progress.update(step, message)
            log_step(f"Pipeline Step: {step.name}", "in progress", message)
            if progress_callback:
                progress_callback(progress)

        try:
            # Step 1: 데이터 수집 (Blocking I/O -> Thread)
            update_progress(PipelineStep.DATA_COLLECTION, "데이터 수집 시작")
            collected_data = await asyncio.to_thread(
                self._collector.collect_all_data,
                product=product,
                config=config,
                progress_callback=update_progress,
            )

            # Step 2: 마케팅 전략 생성 (Blocking I/O -> Thread)
            update_progress(PipelineStep.STRATEGY_GENERATION, "마케팅 전략 생성 중...")
            record_prompt("marketing.analysis")
            strategy = await asyncio.to_thread(
                self._marketing.generate_strategy,
                product=product,
                collected_data=collected_data,
            )

            # Step 3, 4, 2.1: Parallel Execution for Content Generation
            # Define wrapper functions for independent tasks
            async def run_social():
                if config.generate_social:
                    update_progress(
                        PipelineStep.SOCIAL_GENERATION, "SNS 포스팅 생성 중..."
                    )
                    try:
                        record_prompt("social.media.posts")
                        posts = await self._social.generate_posts(
                            product=product,
                            strategy=strategy,
                            top_insights=collected_data.top_insights,
                        )
                        strategy["social_posts"] = posts
                        log_info("SNS 포스팅 생성 완료")
                    except Exception as e:
                        logger.error(f"SNS 포스팅 생성 실패: {e}")
                        log_error(f"SNS 포스팅 생성 중 오류 발생: {e}")

            async def run_thumbnail():
                if config.generate_thumbnail:
                    update_progress(
                        PipelineStep.THUMBNAIL_CREATION, "썸네일 생성 중..."
                    )
                    if config.generate_multi_thumbnails:
                        if config.thumbnail_styles:
                            styles = config.thumbnail_styles[: config.thumbnail_count]
                        else:
                            all_styles = list(THUMBNAIL_STYLES.keys())
                            n = min(config.thumbnail_count, len(all_styles))
                            styles = random.sample(all_styles, n)

                        thumbnails = await asyncio.to_thread(
                            self._thumbnail.generate_from_strategy,
                            product=product,
                            strategy=strategy,
                            count=config.thumbnail_count,
                            styles=styles,
                        )
                        generated_content.multi_thumbnails = thumbnails
                        if thumbnails:
                            generated_content.thumbnail_data = thumbnails[0].get(
                                "image"
                            )
                    else:
                        hooks = strategy.get("hook_suggestions", [])
                        hook_text = (
                            hooks[0] if hooks else f"{product.get('name', '제품')}!"
                        )
                        thumbnail = await asyncio.to_thread(
                            self._thumbnail.generate,
                            product=product,
                            hook_text=hook_text,
                        )
                        generated_content.thumbnail_data = thumbnail

            async def run_video():
                if config.generate_video:
                    update_progress(PipelineStep.VIDEO_GENERATION, "비디오 생성 중...")
                    video_mode = "single"
                    phase2_prompt = None
                    enable_dual_phase_beta = False

                    if config.video_dual_phase_beta:
                        video_mode = "dual"
                        enable_dual_phase_beta = True
                        category = product.get("category", "product")
                        phase2_prompt = (
                            "Freeze frame hero shot of a premium "
                            f"{category} on a clean studio background. "
                            "Soft light leaks, slow zoom in, subtle CTA text."
                        )

                    video_result = await asyncio.to_thread(
                        self._video.generate_marketing_video,
                        product=product,
                        strategy=strategy,
                        duration_seconds=config.video_duration,
                        mode=video_mode,
                        phase2_prompt=phase2_prompt,
                        enable_dual_phase_beta=enable_dual_phase_beta,
                    )

                    if isinstance(video_result, bytes):
                        generated_content.video_bytes = video_result
                    else:
                        generated_content.video_url = video_result

            # Run parallel tasks
            await asyncio.gather(run_social(), run_thumbnail(), run_video())

            # Step 5: Upload (optional)
            if upload_enabled:
                update_progress(PipelineStep.UPLOAD, "Uploading to GCS...")
                upload_status, upload_errors = await asyncio.to_thread(
                    self._upload_to_gcs,
                    product=product,
                    config=config,
                    collected_data=collected_data,
                    strategy=strategy,
                    generated_content=generated_content,
                )

            # 완료
            update_progress(PipelineStep.COMPLETED, "파이프라인 완료!")
            duration = time.time() - start_time
            self._last_duration = duration

            log_success(f"파이프라인 실행 완료 (소요 시간: {duration:.2f}초)")
            log_timing("Pipeline Execution", duration * 1000)

            result = PipelineResult(
                success=True,
                product_name=product.get("name", ""),
                config=config,
                collected_data=collected_data,
                strategy=strategy,
                generated_content=generated_content,
                prompt_log=prompt_log,
                approval_status="draft",
                audit_trail=audit_trail,
                upload_status=upload_status,
                upload_errors=upload_errors,
                duration_seconds=duration,
            )

            # 히스토리 저장
            try:
                save_path = await asyncio.to_thread(self._history.save_result, result)
                log_info(f"파이프라인 결과 저장 완료: {save_path}")
            except Exception as e:
                logger.error(f"파이프라인 결과 저장 실패: {e}")


            if self._rag_ingestion:
                try:
                    await asyncio.to_thread(
                        self._rag_ingestion.ingest_pipeline_result, result
                    )
                except Exception as e:
                    logger.error(f"RAG ingestion failed: {e}")

            return result

        except Exception as e:
            logger.error(f"파이프라인 실행 실패: {e}")
            update_progress(PipelineStep.FAILED, str(e))
            duration = time.time() - start_time
            self._last_duration = duration

            result = PipelineResult(
                success=False,
                product_name=product.get("name", ""),
                config=config,
                collected_data=collected_data,
                strategy=strategy,
                generated_content=generated_content,
                prompt_log=prompt_log,
                approval_status="draft",
                audit_trail=audit_trail,
                upload_status=upload_status,
                upload_errors=upload_errors,
                error_message=str(e),
                duration_seconds=duration,
            )

            # 실패 결과도 저장
            try:
                self._history.save_result(result)
            except Exception as e:
                log_error(f"파이프라인 실패 결과 저장 실패: {e}")

            return result

    def execute_data_collection_only(
        self,
        product: dict,
        config: PipelineConfig,
        progress_callback: Optional[Callable[[str, int], None]] = None,
    ) -> CollectedData:
        """데이터 수집만 실행"""
        logger.info(f"데이터 수집 시작: {product.get('name', 'N/A')}")
        try:
            collected_data = self._collector.collect_all_data(
                product=product,
                config=config,
            )
            return collected_data

        except Exception as e:
            logger.error(f"데이터 수집 실패: {e}")
            raise PipelineError(
                f"데이터 수집 실패: {e}",
                original_error=e,
            )

    def _upload_to_gcs(
        self,
        product: dict,
        config: PipelineConfig,
        collected_data: CollectedData,
        strategy: dict,
        generated_content: GeneratedContent,
    ) -> tuple[UploadStatus, list[str]]:
        """GCS upload (auto bucket creation)."""
        prefix = build_gcs_prefix(product, "pipeline")
        storage = self._storage
        errors: list[str] = []
        total_uploads = 0

        if collected_data:
            total_uploads += 1
            try:
                storage.upload(
                    data=collected_data.model_dump(),
                    path=f"{prefix}/collected_data.json",
                    content_type="application/json",
                )
            except Exception as e:
                log_error(f"GCS collected_data upload failed: {e}")
                errors.append(f"collected_data.json: {e}")

        if strategy:
            total_uploads += 1
            try:
                storage.upload(
                    data=strategy,
                    path=f"{prefix}/strategy.json",
                    content_type="application/json",
                )
            except Exception as e:
                log_error(f"GCS strategy upload failed: {e}")
                errors.append(f"strategy.json: {e}")

        if generated_content.thumbnail_data and not generated_content.multi_thumbnails:
            total_uploads += 1
            try:
                ext = detect_image_ext(generated_content.thumbnail_data)
                thumb_path = f"{prefix}/thumbnail{ext}"
                storage.upload(
                    data=generated_content.thumbnail_data,
                    path=thumb_path,
                    content_type="image/png" if ext == ".png" else "image/jpeg",
                )
                generated_content.thumbnail_url = gcs_url_for(storage, thumb_path)
            except Exception as e:
                log_error(f"GCS thumbnail upload failed: {e}")
                errors.append(f"thumbnail{ext}: {e}")

        if generated_content.multi_thumbnails:
            for idx, item in enumerate(generated_content.multi_thumbnails):
                image_bytes = item.get("image") or item.get("image_bytes")
                if not image_bytes:
                    continue
                total_uploads += 1
                try:
                    ext = detect_image_ext(image_bytes)
                    style_key = (item.get("style") or "thumb").replace(" ", "_")[:20]
                    multi_path = f"{prefix}/thumbnail_{idx + 1}_{style_key}{ext}"
                    storage.upload(
                        data=image_bytes,
                        path=multi_path,
                        content_type="image/png" if ext == ".png" else "image/jpeg",
                    )
                    item["url"] = gcs_url_for(storage, multi_path)
                except Exception as e:
                    log_error(f"GCS thumbnail #{idx + 1} upload failed: {e}")
                    errors.append(f"thumbnail_{idx + 1}{ext}: {e}")

        if generated_content.video_bytes:
            total_uploads += 1
            try:
                ext = detect_video_ext(generated_content.video_bytes)
                video_path = f"{prefix}/video{ext}"
                storage.upload(
                    data=generated_content.video_bytes,
                    path=video_path,
                    content_type="video/mp4"
                    if ext == ".mp4"
                    else "application/octet-stream",
                )
                generated_content.video_url = gcs_url_for(storage, video_path)
            except Exception as e:
                log_error(f"GCS video upload failed: {e}")
                errors.append(f"video{ext}: {e}")

        metadata = {
            "product": product,
            "config": config.model_dump()
            if hasattr(config, "model_dump")
            else dict(config),
            "duration_seconds": getattr(self, "_last_duration", None),
            "thumbnail_url": generated_content.thumbnail_url,
            "video_url": generated_content.video_url,
        }
        total_uploads += 1
        try:
            storage.upload(
                data=metadata,
                path=f"{prefix}/metadata.json",
                content_type="application/json",
            )
        except Exception as e:
            log_error(f"GCS metadata upload failed: {e}")
            errors.append(f"metadata.json: {e}")

        if total_uploads == 0:
            return UploadStatus.SKIPPED, []
        if not errors:
            return UploadStatus.SUCCESS, []
        if len(errors) < total_uploads:
            return UploadStatus.PARTIAL, errors
        return UploadStatus.FAILED, errors
