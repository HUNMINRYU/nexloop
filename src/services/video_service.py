"""
비디오 서비스
AI 기반 마케팅 비디오 생성 비즈니스 로직
"""

import re  # 정규식 모듈 추가
from typing import Any, Callable, Dict, Optional

from core.exceptions import VideoGenerationError
from core.prompts.veo_template import VeoTemplateManager
from infrastructure.clients.veo_client import VeoClient
from utils.logger import log_error, log_info, log_step, log_success


class VideoService:
    """비디오 생성 서비스"""

    def __init__(self, client: VeoClient) -> None:
        self._client = client

    def sanitize_prompt_input(self, text: str) -> str:
        """
        [AI Product Pattern] Prompt Injection 방지 및 특수문자 정화
        - 실행 가능한 코드 패턴, 시스템 명령 등 위험한 패턴 제거
        - LLM 혼란을 주는 제어 문자 제거
        """
        if not text:
            return ""

        # 1. 제어 문자 제거
        sanitized = re.sub(r"[\x00-\x1f\x7f]", "", text)
        sanitized = sanitized.strip()

        # 2. 시스템 프롬프트 오버라이딩 시도 방지 (간단한 키워드 필터링)
        # 실제로는 더 복잡한 로직이 필요하지만, 여기서는 기본적인 것만 차단
        dangerous_patterns = [
            r"ignore previous instructions",
            r"system prompt",
            r"override",
            r"jailbreak",
        ]

        for pattern in dangerous_patterns:
            sanitized = re.sub(pattern, "", sanitized, flags=re.IGNORECASE)

        # 3. 길이 제한 및 공백 정리
        sanitized = re.sub(r"\s+", " ", sanitized)
        max_length = 800
        if len(sanitized) > max_length:
            sanitized = sanitized[:max_length].rstrip()

        return sanitized

    def _validate_prompt_safety(self, prompt: str) -> None:
        """Basic safety scan before sending prompt to Veo."""
        if not prompt:
            return

        blocked_terms = [
            "nsfw",
            "nude",
            "porn",
            "sex",
            "sexual",
            "gore",
            "blood",
            "hate",
            "violent",
            "violence",
        ]
        pattern = r"\b(" + "|".join(map(re.escape, blocked_terms)) + r")\b"
        if re.search(pattern, prompt, flags=re.IGNORECASE):
            raise VideoGenerationError("Unsafe prompt content detected. Please revise.")

    def validate_video_output(self, result: Any) -> bool:
        """
        [AI Product Pattern] 생성된 비디오 출력 유효성 검증
        - bytes: 비어있지 않은지 확인
        - str: 유효한 GCS URL 패턴인지 확인
        """
        if not result:
            return False

        if isinstance(result, bytes):
            return len(result) > 1024  # 최소 1KB 이상이어야 유효

        if isinstance(result, str):
            # GCS URL 패턴 또는 로컬 경로 체크
            # 예: https://storage.googleapis.com/... 또는 /path/to/video
            return (
                result.startswith("http") or result.startswith("/") or "gs://" in result
            )

        return False

    def generate(
        self,
        prompt: str,
        duration_seconds: int = 8,
        resolution: str = "720p",
        mode: str = "single",
        phase2_prompt: Optional[str] = None,
        enable_dual_phase_beta: bool = False,
        progress_callback: Optional[Callable[[str, int], None]] = None,
    ) -> bytes | str:
        """비디오 생성"""
        # [Defense] 입력값 정화
        safe_prompt = self.sanitize_prompt_input(prompt)
        self._validate_prompt_safety(safe_prompt)
        log_step("비디오 생성 요청", "시작", f"{duration_seconds}s, {resolution}")

        try:
            if mode == "dual":
                if not enable_dual_phase_beta:
                    raise VideoGenerationError(
                        "Dual phase generation requires beta flag."
                    )
                if not phase2_prompt:
                    raise VideoGenerationError(
                        "Dual phase generation requires phase2_prompt."
                    )

                safe_phase2 = self.sanitize_prompt_input(phase2_prompt)
                self._validate_prompt_safety(safe_phase2)

                if hasattr(self._client, "generate_video_with_fallback"):
                    result = self._client.generate_video_with_fallback(
                        phase1_prompt=safe_prompt,
                        phase2_prompt=safe_phase2,
                        duration_seconds=duration_seconds,
                        resolution=resolution,
                        progress_callback=progress_callback,
                    )
                else:
                    phase1_result = self._client.generate_video(
                        prompt=safe_prompt,
                        duration_seconds=duration_seconds,
                        resolution=resolution,
                        progress_callback=progress_callback,
                    )
                    try:
                        result = self._client.generate_video(
                            prompt=safe_phase2,
                            duration_seconds=duration_seconds,
                            resolution=resolution,
                            progress_callback=progress_callback,
                        )
                    except Exception:
                        result = phase1_result
            else:
                result = self._client.generate_video(
                    prompt=safe_prompt,
                    duration_seconds=duration_seconds,
                    resolution=resolution,
                    progress_callback=progress_callback,
                )

            # [Defense] 출력 검증
            if not self.validate_video_output(result):
                raise VideoGenerationError("생성된 비디오 데이터가 유효하지 않습니다.")

            if isinstance(result, bytes):
                log_success(f"비디오 생성 완료 ({len(result)} bytes)")
            else:
                log_info(f"비디오 생성 상태: {result[:100]}")

            return result

        except Exception as e:
            log_error(f"비디오 생성 서비스 실패: {e}")
            raise VideoGenerationError(
                f"비디오 생성 실패: {e}",
                original_error=e,
            )

    def generate_from_image(
        self,
        image_bytes: bytes,
        prompt: str,
        duration_seconds: int = 8,
        progress_callback: Optional[Callable[[str, int], None]] = None,
    ) -> bytes | None:
        """이미지 기반 비디오 생성 (Image-to-Video)"""
        # [Defense] 입력값 정화
        safe_prompt = self.sanitize_prompt_input(prompt)
        self._validate_prompt_safety(safe_prompt)
        log_step("I2V 생성 요청", "시작", f"{duration_seconds}s")

        try:
            result = self._client.generate_video_from_image(
                image_bytes=image_bytes,
                prompt=safe_prompt,
                duration_seconds=duration_seconds,
                progress_callback=progress_callback,
            )

            # [Defense] 출력 검증
            if result and not self.validate_video_output(result):
                log_error(
                    "I2V 생성 결과 유효성 검증 실패 (파일 크기가 너무 작거나 잘못된 URL)"
                )
                return None

            if result:
                if isinstance(result, bytes):
                    log_success(f"I2V 생성 완료 ({len(result)} bytes)")
                else:
                    log_info(f"I2V 생성 결과: {result[:100]}")

            return result

        except Exception as e:
            log_error(f"I2V 생성 서비스 실패: {e}")
            raise VideoGenerationError(
                f"이미지 기반 비디오 생성 실패: {e}",
                original_error=e,
            )

    def generate_story_prompt_from_image(
        self,
        image_bytes: bytes,
        product: Dict[str, Any],
        hook_text: str,
        mode: str = "single",  # single or dual
    ) -> str:
        """
        [Vision-Narrative Bridge]
        썸네일 이미지를 분석하고 마케팅 서사를 입혀 최적화된 Veo 프롬프트 생성
        """
        log_step("Vision-Narrative", "프롬프트 생성", f"Mode: {mode}")

        try:
            # 1. 템플릿 로드
            system_prompt = VeoTemplateManager.get_system_prompt()
            template = VeoTemplateManager.get_template(mode)

            # 2. Gemini VIsion 호출 (client 메서드 가정, 실제 구현 필요)
            # 현재 client에 vision 기능이 명시적으로 없으므로, LLM 호출을 통한
            # 멀티모달 프롬프트 생성을 client에 위임하거나 여기서 직접 호출해야 함.
            # *client.generate_multimodal_prompt 메서드가 존재한다고 가정*
            # 만약 없다면 인프라 계층에 추가가 필요하지만, 일단 client 메서드로 추상화
            prompt = self._client.generate_multimodal_prompt(
                system_instruction=system_prompt,
                user_instruction=f"""
                Context:
                - Product: {product.get("name")} ({product.get("description")})
                - Hook: {hook_text}
                - Target Template:
                {template}

                Task:
                Analyze the attached image (thumbnail) as the 'Start Frame'.
                Fill in the template to create a cohesive video narrative starting from this visual.
                """,
                image_bytes=image_bytes,
            )

            log_success("Vision-Narrative 프롬프트 생성 완료")
            return prompt

        except Exception as e:
            log_error(f"스토리 프롬프트 생성 실패: {e}")
            # 실패 시 기본 템플릿 반환 (Fallback)
            return f"Cinematic video of {product.get('name')}, {hook_text}, high quality, 4k"

    def create_marketing_prompt(
        self,
        product: dict,
        insights: dict,
        hook_text: str = "",
    ) -> str:
        """마케팅 비디오 프롬프트 생성"""
        return self._client.generate_marketing_prompt(
            product=product,
            insights=insights,
            hook_text=hook_text,
        )

    def generate_marketing_video(
        self,
        product: dict,
        strategy: dict,
        duration_seconds: int = 8,
        mode: str = "single",
        phase2_prompt: Optional[str] = None,
        enable_dual_phase_beta: bool = False,
        progress_callback: Optional[Callable[[str, int], None]] = None,
    ) -> bytes | str:
        """마케팅 비디오 생성"""
        p_name = product.get("name", "N/A")
        log_step("마케팅 비디오 생성", "시작", f"제품: {p_name}")

        # 전략에서 훅 텍스트 추출
        hooks = strategy.get("hook_suggestions", [])
        hook_text = hooks[0] if hooks else f"{product.get('name', '제품')}!"

        # 인사이트 구성
        insights = {
            "hook": hook_text,
            "style": "commercial",
            "mood": "dramatic",
        }

        # 프롬프트 생성
        prompt = self.create_marketing_prompt(product, insights, hook_text)

        # 비디오 생성
        return self.generate(
            prompt=prompt,
            duration_seconds=duration_seconds,
            mode=mode,
            phase2_prompt=phase2_prompt,
            enable_dual_phase_beta=enable_dual_phase_beta,
            progress_callback=progress_callback,
        )

    def get_available_motions(self) -> list[str]:
        """사용 가능한 카메라 모션 목록"""
        return self._client.get_available_motions()

    def generate_multi_prompts(
        self,
        product: dict,
        base_hook: str,
        duration_seconds: int = 8,
    ) -> list[dict]:
        """다양한 스타일의 비디오 프롬프트 생성"""
        return self._client.generate_multi_video_prompts(
            product=product,
            base_hook=base_hook,
            duration_seconds=duration_seconds,
        )
