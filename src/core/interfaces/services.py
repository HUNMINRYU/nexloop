"""
서비스 인터페이스 정의
"""

from typing import Any, Callable, Optional, Protocol, runtime_checkable

from core.models import CollectedData, PipelineConfig, PipelineProgress, PipelineResult


@runtime_checkable
class IYouTubeService(Protocol):
    def search_videos(self, query: str, max_results: int = 3) -> list[dict]:
        ...

    def collect_product_data(
        self,
        product: dict,
        max_results: int = 5,
        include_comments: bool = True,
        progress_callback: Optional[Callable[[str, int], None]] = None,
    ) -> dict:
        ...

    def analyze_comments(self, comments: list[dict]) -> dict:
        ...


@runtime_checkable
class INaverService(Protocol):
    def search_products(self, query: str, max_results: int = 10) -> list[dict]:
        ...

    def collect_product_data(
        self,
        product: dict,
        max_results: int = 10,
        progress_callback: Optional[Callable[[str, int], None]] = None,
    ) -> dict:
        ...

    def analyze_competitors(self, products: list[dict]) -> dict:
        ...


@runtime_checkable
class IMarketingService(Protocol):
    def analyze_data(
        self,
        youtube_data: dict,
        naver_data: dict,
        product_name: str,
        market_trends: dict | None = None,
        progress_callback: Optional[Callable[[str, int], None]] = None,
        use_grounding: bool = True,
    ) -> dict[str, Any]:
        ...

    def generate_strategy(
        self,
        product: dict,
        collected_data: CollectedData,
        progress_callback: Optional[Callable[[str, int], None]] = None,
    ) -> dict[str, Any]:
        ...

    def generate_hooks(
        self,
        product_name: str,
        hook_types: list[str] | None = None,
        count: int = 5,
    ) -> list[dict]:
        ...

    def extract_key_insights(self, strategy: dict) -> dict:
        ...


@runtime_checkable
class IThumbnailService(Protocol):
    def generate(
        self,
        product: dict,
        hook_text: str,
        style: str = "neobrutalism",
        include_text_overlay: bool = False,
        progress_callback: Optional[Callable[[str, int], None]] = None,
    ) -> bytes | None:
        ...

    def generate_multiple(
        self,
        product: dict,
        hook_texts: list[str],
        styles: list[str] | None = None,
        progress_callback: Optional[Callable[[str, int], None]] = None,
    ) -> list[dict]:
        ...

    def generate_from_strategy(
        self,
        product: dict,
        strategy: dict,
        count: int = 3,
        progress_callback: Optional[Callable[[str, int], None]] = None,
    ) -> list[dict]:
        ...

    def generate_ab_test_set(
        self,
        product: dict,
        hook_text: str,
        styles: list[str] = None,
        progress_callback: Optional[Callable[[str, int], None]] = None,
    ) -> list[dict]:
        ...


@runtime_checkable
class IVideoService(Protocol):
    def generate(
        self,
        prompt: str,
        duration_seconds: int = 8,
        resolution: str = "720p",
        progress_callback: Optional[Callable[[str, int], None]] = None,
    ) -> bytes | str:
        ...

    def generate_marketing_video(
        self,
        product: dict,
        strategy: dict,
        duration_seconds: int = 8,
        progress_callback: Optional[Callable[[str, int], None]] = None,
    ) -> bytes | str:
        ...

    def get_available_motions(self) -> list[str]:
        ...

    def generate_multi_prompts(
        self,
        product: dict,
        base_hook: str,
        duration_seconds: int = 8,
    ) -> list[dict]:
        ...


@runtime_checkable
class IPipelineService(Protocol):
    def execute(
        self,
        product: dict,
        config: PipelineConfig,
        progress_callback: Optional[Callable[[PipelineProgress], None]] = None,
    ) -> PipelineResult:
        ...

    def execute_data_collection_only(
        self,
        product: dict,
        config: PipelineConfig,
        progress_callback: Optional[Callable[[str, int], None]] = None,
    ) -> CollectedData:
        ...


@runtime_checkable
class IHookService(Protocol):
    def get_available_styles(self) -> list[dict]:
        ...

    def generate_hooks(
        self,
        style: str,
        product: dict,
        pain_points: list[str] = None,
        count: int = 3,
    ) -> list[str]:
        ...

    def generate_multi_style_hooks(
        self,
        product: dict,
        pain_points: list[str] = None,
        styles: list[str] = None,
    ) -> dict[str, list[str]]:
        ...

    def get_best_hooks_for_video(
        self,
        product: dict,
        video_style: str = "dramatic",
        pain_points: list[str] = None,
    ) -> list[dict]:
        ...


@runtime_checkable
class ICommentAnalysisService(Protocol):
    def analyze_comments(self, comments: list[dict]) -> dict:
        ...

    def analyze_with_ai(self, comments: list[dict]) -> dict:
        ...

    def get_marketing_phrases(self, comments: list[dict]) -> list[str]:
        ...


@runtime_checkable
class ICTRPredictor(Protocol):
    def predict_ctr(
        self,
        title: str,
        thumbnail_description: str = "",
        competitor_titles: list[str] = None,
        category: str = "general",
    ) -> dict:
        ...

    def compare_variations(self, variations: list[dict]) -> list[dict]:
        ...

    async def predict_with_ai(
        self,
        title: str,
        thumbnail_bytes: bytes = None,
        category: str = "general",
    ) -> dict:
        ...


@runtime_checkable
class IExportService(Protocol):
    def export_pdf(self, data: dict, output_path: str) -> str:
        ...

    def export_notion(self, data: dict, parent_page_id: str = None) -> str:
        ...


@runtime_checkable
class IHistoryService(Protocol):
    def get_history_list(self) -> list[dict[str, Any]]:
        ...

    def load_history(self, history_id: str) -> Optional[PipelineResult]:
        ...

    def delete_history(self, history_id: str) -> bool:
        ...

    def save_result(self, result: PipelineResult) -> str:
        ...


@runtime_checkable
class ISocialMediaService(Protocol):
    async def generate_posts(
        self,
        product: dict,
        strategy: dict,
        top_insights: list[dict] = None,
        platforms: list[str] = None,
    ) -> dict[str, Any]:
        """SNS 채널별 포스팅 문구 생성"""
        ...
