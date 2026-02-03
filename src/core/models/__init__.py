"""
도메인 모델 패키지
모든 Pydantic 모델을 중앙 export
"""
from .marketing import (
    CompetitorAnalysis,
    ContentStrategy,
    HookingPoint,
    MarketTrend,
    MarketingStrategy,
    ShortformScenario,
    SNSCopy,
    TargetPersona,
)
from .chatbot import (
    ChatMessage,
    ChatSession,
)
from .naver import (
    CompetitorStats,
    NaverProduct,
    NaverSearchResult,
)
from .pipeline import (
    CollectedData,
    GeneratedContent,
    PipelineConfig,
    PipelineProgress,
    PipelineResult,
    PipelineStep,
    UploadStatus,
)
from .product import (
    Product,
    ProductCatalog,
    ProductCategory,
)
from .youtube import (
    GainPoint,
    PainPoint,
    YouTubeComment,
    YouTubeSearchResult,
    YouTubeVideo,
)

__all__ = [
    # Product
    "Product",
    "ProductCatalog",
    "ProductCategory",
    # Chatbot
    "ChatMessage",
    "ChatSession",
    # YouTube
    "YouTubeVideo",
    "YouTubeComment",
    "YouTubeSearchResult",
    "PainPoint",
    "GainPoint",
    # Naver
    "NaverProduct",
    "NaverSearchResult",
    "CompetitorStats",
    # Marketing
    "TargetPersona",
    "HookingPoint",
    "ShortformScenario",
    "SNSCopy",
    "CompetitorAnalysis",
    "ContentStrategy",
    "MarketTrend",
    "MarketingStrategy",
    # Pipeline
    "PipelineStep",
    "PipelineConfig",
    "PipelineProgress",
    "PipelineResult",
    "CollectedData",
    "GeneratedContent",
    "UploadStatus",
]
