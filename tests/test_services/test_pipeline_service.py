from core.models import PipelineConfig
from services.data_collection_service import DataCollectionService
from services.marketing_service import MarketingService
from services.naver_service import NaverService
from services.pipeline_service import PipelineService
from services.youtube_service import YouTubeService


def test_pipeline_service_execute_minimal(
    sample_product,
    mock_gemini_client,
    mock_youtube_client,
    mock_naver_client,
    mock_storage_service,
    mock_pipeline_orchestrator,
    mock_social_service,
    mock_thumbnail_service,
    mock_video_service,
    mock_history_service,
):
    youtube_service = YouTubeService(client=mock_youtube_client)
    naver_service = NaverService(client=mock_naver_client)
    marketing_service = MarketingService(client=mock_gemini_client)

    collector = DataCollectionService(
        youtube_service=youtube_service,
        naver_service=naver_service,
        pipeline_orchestrator=mock_pipeline_orchestrator,
    )

    service = PipelineService(
        data_collection_service=collector,
        marketing_service=marketing_service,
        thumbnail_service=mock_thumbnail_service,
        video_service=mock_video_service,
        storage_service=mock_storage_service,
        history_service=mock_history_service,
        social_media_service=mock_social_service,
    )

    config = PipelineConfig(
        generate_social=False,
        generate_thumbnail=False,
        generate_video=False,
        upload_to_gcs=False,
    )

    result = service.execute(product=sample_product, config=config)
    assert result.success is True
    assert result.product_name == sample_product["name"]
    assert result.collected_data is not None
