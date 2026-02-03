import pytest

from core.exceptions import DataCollectionError
from services.youtube_service import YouTubeService


def test_youtube_service_search_videos(mock_youtube_client):
    service = YouTubeService(client=mock_youtube_client)
    results = service.search_videos("테스트", max_results=1)
    assert results[0]["id"] == "vid1"


def test_youtube_service_collect_product_data(mock_youtube_client, sample_product):
    service = YouTubeService(client=mock_youtube_client)
    progress_calls = []

    def progress(message, percentage):
        progress_calls.append((message, percentage))

    data = service.collect_product_data(
        product=sample_product,
        max_results=1,
        include_comments=True,
        progress_callback=progress,
    )
    assert "videos" in data
    assert progress_calls[-1][1] == 100


def test_youtube_service_collect_product_data_error(sample_product):
    class FailingClient:
        def collect_video_data(self, **kwargs):
            raise RuntimeError("fail")

    service = YouTubeService(client=FailingClient())
    with pytest.raises(DataCollectionError):
        service.collect_product_data(product=sample_product)
