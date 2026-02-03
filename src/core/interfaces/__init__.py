"""
인터페이스 (Protocol) 패키지
의존성 역전 원칙(DIP)을 위한 추상화 레이어
"""
from .ai_service import (
    IImageGenerationService,
    IMarketingAIService,
    ITextGenerationService,
)
from .api_client import (
    IApiClient,
    INaverClient,
    ISearchClient,
    IYouTubeClient,
)
from .chatbot import (
    IChatbotService,
    IRAGClient,
)
from .services import (
    ICommentAnalysisService,
    ICTRPredictor,
    IExportService,
    IHookService,
    IMarketingService,
    INaverService,
    IPipelineService,
    IThumbnailService,
    IVideoService,
    IYouTubeService,
)
from .storage import IStorageService
from .video_generator import IVideoGenerator

__all__ = [
    # API Clients
    "IApiClient",
    "ISearchClient",
    "IYouTubeClient",
    "INaverClient",
    # Chatbot
    "IChatbotService",
    "IRAGClient",
    # AI Services
    "ITextGenerationService",
    "IImageGenerationService",
    "IMarketingAIService",
    # Storage
    "IStorageService",
    # Video
    "IVideoGenerator",
    # Services
    "IYouTubeService",
    "INaverService",
    "IMarketingService",
    "IThumbnailService",
    "IVideoService",
    "IPipelineService",
    "IHookService",
    "ICommentAnalysisService",
    "ICTRPredictor",
    "IExportService",
]
