"""
Dependency Injection Container
"""

from __future__ import annotations

from contextlib import contextmanager
from functools import cached_property
from typing import TYPE_CHECKING, ClassVar, Iterator, Optional

from config.settings import get_settings
from core.interfaces.ai_service import IMarketingAIService
from core.interfaces.chatbot import IChatbotService, IRAGClient
from core.interfaces.api_client import INaverClient, IYouTubeClient
from core.interfaces.services import (
    ICommentAnalysisService,
    ICTRPredictor,
    IExportService,
    IHistoryService,
    IHookService,
    IMarketingService,
    INaverService,
    IPipelineService,
    IThumbnailService,
    IVideoService,
    IYouTubeService,
)
from core.interfaces.storage import IStorageService
from infrastructure.clients.discovery_engine_client import DiscoveryEngineClient
from infrastructure.clients.gemini_client import GeminiClient
from infrastructure.clients.naver_client import NaverClient
from infrastructure.clients.veo_client import VeoClient
from infrastructure.clients.youtube_client import YouTubeClient
from infrastructure.storage.gcs_storage import GCSStorage
from services.chatbot_service import ChatbotService
from services.data_collection_service import DataCollectionService
from services.history_service import HistoryService
from services.marketing_service import MarketingService
from services.market_trend_service import MarketTrendService
from services.naver_service import NaverService
from services.pipeline.orchestrator import PipelineOrchestrator
from services.pipeline.stages.filter import QualityFilter
from services.pipeline.stages.hydration import FeatureHydrator
from services.pipeline.stages.scorer import EngagementScorer
from services.pipeline.stages.selector import TopInsightSelector
from services.pipeline.stages.source import CommentSource
from services.pipeline_service import PipelineService
from services.rag_ingestion_service import RagIngestionService
from services.thumbnail_service import ThumbnailService
from services.video_service import VideoService
from services.youtube_service import YouTubeService
from services.auth_service import AuthService

if TYPE_CHECKING:
    from services.comment_analysis_service import CommentAnalysisService
    from services.ctr_predictor import CTRPredictor
    from services.export_service import ExportService
from services.hook_service import HookService
from services.social_service import SocialMediaService
from services.insight_external_service import InsightExternalService
from services.insight_report_service import InsightReportService


class ServiceContainer:
    """서비스 컨테이너 (Singleton + Lazy Factory)"""

    _instance: ClassVar[Optional["ServiceContainer"]] = None

    def __init__(self, settings=None, overrides: Optional[dict[str, object]] = None):
        self._settings = settings or get_settings()
        self._overrides = overrides or {}

    @classmethod
    def get_instance(cls) -> "ServiceContainer":
        if cls._instance is None:
            cls._instance = ServiceContainer()
        return cls._instance

    @classmethod
    def set_instance(cls, instance: Optional["ServiceContainer"]) -> None:
        cls._instance = instance

    def clear_cache(self) -> None:
        for name in (
            "youtube_client",
            "naver_client",
            "gemini_client",
            "veo_client",
            "storage_service",
            "youtube_service",
            "naver_service",
            "marketing_service",
            "thumbnail_service",
            "video_service",
            "hook_service",
            "comment_analysis_service",
            "ctr_predictor",
            "export_service",
            "pipeline_service",
            "auth_service",
            "discovery_engine_client",
            "chatbot_service",
            "data_collection_service",
            "market_trend_service",
            "rag_ingestion_service",
            "insight_external_service",
            "insight_report_service",
        ):
            self.__dict__.pop(name, None)

    def _get_override(self, key: str, protocol=None):
        value = self._overrides.get(key)
        if value is None:
            return None
        if protocol and not isinstance(value, protocol):
            raise TypeError(f"Override for {key} does not implement {protocol.__name__}")
        return value

    # Clients
    @cached_property
    def youtube_client(self) -> IYouTubeClient:
        override = self._get_override("youtube_client", IYouTubeClient)
        if override is not None:
            return override
        return YouTubeClient(api_key=self._settings.google_api_key)

    @cached_property
    def naver_client(self) -> INaverClient:
        override = self._get_override("naver_client", INaverClient)
        if override is not None:
            return override
        return NaverClient(
            client_id=self._settings.naver.client_id.get_secret_value(),
            client_secret=self._settings.naver.client_secret.get_secret_value(),
        )

    @cached_property
    def gemini_client(self) -> IMarketingAIService:
        override = self._get_override("gemini_client", IMarketingAIService)
        if override is not None:
            return override
        return GeminiClient(
            project_id=self._settings.gcp.project_id,
            location=self._settings.gcp.location,
        )

    @cached_property
    def discovery_engine_client(self) -> IRAGClient:
        override = self._get_override("discovery_engine_client", IRAGClient)
        if override is not None:
            return override
        return DiscoveryEngineClient(
            project_id=self._settings.gcp.project_id,
            location=self._settings.gcp.location,
            data_store_id=self._settings.gcp.data_store_id,
        )

    @cached_property
    def veo_client(self) -> VeoClient:
        return VeoClient(
            project_id=self._settings.gcp.project_id,
            location=self._settings.gcp.location,
            gcs_bucket_name=self._settings.gcp.gcs_bucket_name or "",
            model_id=self._settings.models.veo_model_id,
            vision_model_id=self._settings.models.gemini_text_model,
        )

    # Storage
    @cached_property
    def storage_service(self) -> IStorageService:
        override = self._get_override("storage_service", IStorageService)
        if override is not None:
            return override
        return GCSStorage(
            bucket_name=self._settings.gcp.gcs_bucket_name,
            project_id=self._settings.gcp.project_id,
            location=self._settings.gcp.location,
        )

    # Services
    @cached_property
    def youtube_service(self) -> YouTubeService:
        override = self._get_override("youtube_service", IYouTubeService)
        if override is not None:
            return override
        return YouTubeService(client=self.youtube_client)

    @cached_property
    def naver_service(self) -> NaverService:
        override = self._get_override("naver_service", INaverService)
        if override is not None:
            return override
        return NaverService(client=self.naver_client)

    @cached_property
    def marketing_service(self) -> MarketingService:
        override = self._get_override("marketing_service", IMarketingService)
        if override is not None:
            return override
        return MarketingService(client=self.gemini_client)

    @cached_property
    def market_trend_service(self) -> MarketTrendService:
        return MarketTrendService(rag_client=self.discovery_engine_client)

    @cached_property
    def thumbnail_service(self) -> ThumbnailService:
        override = self._get_override("thumbnail_service", IThumbnailService)
        if override is not None:
            return override
        return ThumbnailService(client=self.gemini_client)

    @cached_property
    def video_service(self) -> VideoService:
        override = self._get_override("video_service", IVideoService)
        if override is not None:
            return override
        return VideoService(client=self.veo_client)

    @cached_property
    def hook_service(self) -> "HookService":
        override = self._get_override("hook_service", IHookService)
        if override is not None:
            return override
        from services.hook_service import HookService

        return HookService(gemini_client=self.gemini_client)

    @cached_property
    def comment_analysis_service(self) -> "CommentAnalysisService":
        override = self._get_override(
            "comment_analysis_service", ICommentAnalysisService
        )
        if override is not None:
            return override
        from services.comment_analysis_service import CommentAnalysisService

        return CommentAnalysisService(gemini_client=self.gemini_client)

    @cached_property
    def ctr_predictor(self) -> "CTRPredictor":
        override = self._get_override("ctr_predictor", ICTRPredictor)
        if override is not None:
            return override
        from services.ctr_predictor import CTRPredictor

        return CTRPredictor(gemini_client=self.gemini_client)

    @cached_property
    def export_service(self) -> "ExportService":
        override = self._get_override("export_service", IExportService)
        if override is not None:
            return override
        from services.export_service import ExportService

        return ExportService(settings=self._settings)

    @cached_property
    def history_service(self) -> HistoryService:
        override = self._get_override("history_service", IHistoryService)
        if override is not None:
            return override
        return HistoryService()

    @cached_property
    def social_media_service(self) -> SocialMediaService:
        from services.social_service import SocialMediaService

        return SocialMediaService(gemini_client=self.gemini_client)

    @cached_property
    def pipeline_orchestrator(self) -> PipelineOrchestrator:
        return PipelineOrchestrator(
            source=CommentSource(),
            hydrator=FeatureHydrator(self.gemini_client),
            quality_filter=QualityFilter(),
            scorer=EngagementScorer(),
            selector=TopInsightSelector(),
        )

    @cached_property
    def data_collection_service(self) -> DataCollectionService:
        return DataCollectionService(
            youtube_service=self.youtube_service,
            naver_service=self.naver_service,
            pipeline_orchestrator=self.pipeline_orchestrator,
            market_trend_service=self.market_trend_service,
        )

    @cached_property
    def pipeline_service(self) -> PipelineService:
        override = self._get_override("pipeline_service", IPipelineService)
        if override is not None:
            return override
        return PipelineService(
            data_collection_service=self.data_collection_service,
            marketing_service=self.marketing_service,
            thumbnail_service=self.thumbnail_service,
            video_service=self.video_service,
            storage_service=self.storage_service,
            history_service=self.history_service,
            social_media_service=self.social_media_service,
            rag_ingestion_service=self.rag_ingestion_service,
        )

    @cached_property
    def auth_service(self) -> AuthService:
        override = self._get_override("auth_service")
        if override is not None:
            return override
        return AuthService(
            secret=self._settings.app.jwt_secret,
            expire_hours=self._settings.app.jwt_expire_hours,
        )

    @cached_property
    def chatbot_service(self) -> IChatbotService:
        override = self._get_override("chatbot_service", IChatbotService)
        if override is not None:
            return override
        return ChatbotService(
            gemini_client=self.gemini_client,
            rag_client=self.discovery_engine_client,
        )

    @cached_property
    def rag_ingestion_service(self) -> RagIngestionService:
        return RagIngestionService(rag_client=self.discovery_engine_client)

    @cached_property
    def insight_external_service(self) -> InsightExternalService:
        return InsightExternalService(
            naver_service=self.naver_service,
            rag_ingestion_service=self.rag_ingestion_service,
        )

    @cached_property
    def insight_report_service(self) -> InsightReportService:
        return InsightReportService(
            rag_client=self.discovery_engine_client,
            rag_ingestion=self.rag_ingestion_service,
        )


def get_services() -> ServiceContainer:
    """서비스 컨테이너 반환"""
    return ServiceContainer.get_instance()


@contextmanager
def override_services(
    overrides: Optional[dict[str, object]] = None,
    settings=None,
) -> Iterator[ServiceContainer]:
    """테스트/스크립트용 서비스 오버라이드 컨텍스트"""
    previous = ServiceContainer.get_instance() if ServiceContainer._instance else None
    container = ServiceContainer(settings=settings, overrides=overrides)
    ServiceContainer.set_instance(container)
    try:
        yield container
    finally:
        ServiceContainer.set_instance(previous)
