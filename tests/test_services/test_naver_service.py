import pytest

from core.exceptions import DataCollectionError
from services.naver_service import NaverService
from utils.cache import clear_all_api_cache


def test_naver_service_collect_product_data(mock_naver_client, sample_product):
    service = NaverService(client=mock_naver_client)
    result = service.collect_product_data(product=sample_product, max_results=1)
    assert result["total_count"] == 1
    assert result["competitor_stats"]["min_price"] == 1000


def test_naver_service_collect_product_data_error(sample_product):
    clear_all_api_cache()

    class FailingClient:
        def search_shopping(self, *args, **kwargs):
            raise RuntimeError("fail")

        def analyze_competitors(self, products):
            return {}

        def search_blog(self, *args, **kwargs):
            return []

        def search_news(self, *args, **kwargs):
            return []

    service = NaverService(client=FailingClient())
    with pytest.raises(DataCollectionError):
        service.collect_product_data(product=sample_product, max_results=1)
