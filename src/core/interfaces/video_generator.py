"""
비디오 생성 서비스 인터페이스 정의
"""
from abc import abstractmethod
from typing import Callable, Optional, Protocol, runtime_checkable


@runtime_checkable
class IVideoGenerator(Protocol):
    """비디오 생성 서비스 프로토콜"""

    @abstractmethod
    def generate_video(
        self,
        prompt: str,
        duration_seconds: int = 8,
        resolution: str = "720p",
        progress_callback: Optional[Callable[[str, int], None]] = None,
    ) -> bytes | str:
        """텍스트 프롬프트로 비디오 생성"""
        ...

    @abstractmethod
    def generate_video_from_image(
        self,
        image_bytes: bytes,
        prompt: str,
        duration_seconds: int = 8,
        progress_callback: Optional[Callable[[str, int], None]] = None,
    ) -> bytes | None:
        """이미지 기반 비디오 생성"""
        ...

    @abstractmethod
    def get_available_motions(self) -> list[str]:
        """사용 가능한 카메라 모션 목록"""
        ...

    @abstractmethod
    def generate_marketing_prompt(
        self,
        product: dict,
        insights: dict,
        hook_text: str = "",
    ) -> str:
        """마케팅용 비디오 프롬프트 생성"""
        ...
