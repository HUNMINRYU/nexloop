import pytest

from core.exceptions import StrategyGenerationError
from core.models import CollectedData
from services.marketing_service import MarketingService


def test_marketing_service_analyze_data_success(mock_gemini_client):
    service = MarketingService(client=mock_gemini_client)
    result = service.analyze_data(
        youtube_data={},
        naver_data={},
        product_name="테스트",
        top_insights=[],
    )
    assert result["summary"] == "ok"


def test_marketing_service_analyze_data_error(mock_gemini_client_error):
    service = MarketingService(client=mock_gemini_client_error)
    with pytest.raises(StrategyGenerationError):
        service.analyze_data(
            youtube_data={},
            naver_data={},
            product_name="테스트",
            top_insights=[],
        )


def test_marketing_service_generate_strategy_error(mock_gemini_client_error):
    service = MarketingService(client=mock_gemini_client_error)
    with pytest.raises(StrategyGenerationError):
        service.generate_strategy(product={}, collected_data=CollectedData())
