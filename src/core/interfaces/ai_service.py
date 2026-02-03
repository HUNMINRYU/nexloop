"""
AI 서비스 인터페이스 정의
"""
from abc import abstractmethod
from typing import Any, Callable, Optional, Protocol, runtime_checkable


@runtime_checkable
class ITextGenerationService(Protocol):
    """텍스트 생성 AI 서비스 프로토콜"""

    @abstractmethod
    def generate_text(
        self,
        prompt: str,
        temperature: float = 0.7,
        use_grounding: bool = False,
    ) -> str:
        """텍스트 생성"""
        ...

    @abstractmethod
    async def generate_content_async(
        self,
        prompt: str,
    ) -> str:
        """??? ??? ??"""
        ...


@runtime_checkable
class IImageGenerationService(Protocol):
    """이미지 생성 AI 서비스 프로토콜"""

    @abstractmethod
    def generate_image(
        self,
        prompt: str,
        aspect_ratio: str = "16:9",
    ) -> bytes | None:
        """이미지 생성"""
        ...


@runtime_checkable
class IMarketingAIService(ITextGenerationService, IImageGenerationService, Protocol):
    """마케팅 AI 서비스 통합 프로토콜"""

    @abstractmethod
    def analyze_marketing_data(
        self,
        youtube_data: dict,
        naver_data: dict,
        product_name: str,
        top_insights: list[dict] = None,
        market_trends: dict | None = None,
        progress_callback: Optional[Callable[[str, int], None]] = None,
        use_search_grounding: bool = True,
    ) -> dict[str, Any]:
        """마케팅 데이터 분석"""
        ...

    @abstractmethod
    def generate_marketing_strategy(
        self,
        collected_data: dict,
        progress_callback: Optional[Callable[[str, int], None]] = None,
    ) -> dict[str, Any]:
        """마케팅 전략 생성"""
        ...

    @abstractmethod
    def generate_thumbnail(
        self,
        product: dict,
        hook_text: str,
        style: str = "????",
        style_modifier: Optional[str] = None,
        progress_callback: Optional[Callable[[str, int], None]] = None,
    ) -> bytes | None:
        """??? ??? ??"""
        ...

    @abstractmethod
    def generate_multiple_thumbnails(
        self,
        product: dict,
        hook_texts: list[str],
        styles: list[str] | None = None,
        progress_callback: Optional[Callable[[str, int], None]] = None,
    ) -> list[dict]:
        """다중 썸네일 생성"""
        ...

    @abstractmethod
    def generate_hook_texts(
        self,
        product_name: str,
        hook_types: list[str] | None = None,
        count: int = 5,
        custom_params: dict | None = None,
    ) -> list[dict]:
        """훅 텍스트 생성"""
        ...
