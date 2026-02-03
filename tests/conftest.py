"""공통 테스트 픽스처"""
from __future__ import annotations

from typing import Any

import pytest


class MockGeminiClient:
    def __init__(self, error_mode: bool = False) -> None:
        self.error_mode = error_mode

    def analyze_marketing_data(self, **kwargs) -> dict[str, Any]:
        if self.error_mode:
            return {"error": "analysis failed"}
        return {"summary": "ok", "keywords": ["k1", "k2"]}

    def generate_marketing_strategy(self, **kwargs) -> dict[str, Any]:
        if self.error_mode:
            return {"error": "strategy failed"}
        return {"summary": "strategy ok", "hook_suggestions": ["hook"]}

    def generate_hook_texts(self, **kwargs) -> list[dict]:
        return [{"text": "hook", "type": "loss_aversion"}]

    def generate_text(self, prompt: str, temperature: float = 0.7, use_grounding: bool = False) -> str:
        return '{"answer": "ok", "card": null}'

    async def generate_content_async(self, prompt: str) -> str:
        return "ok"

    def generate_image(self, prompt: str, aspect_ratio: str = "16:9") -> bytes | None:
        return b"image"

    def generate_thumbnail(self, product: dict, hook_text: str, style: str = "dramatic", style_modifier: str | None = None, progress_callback=None) -> bytes | None:
        return b"thumb"

    def generate_multiple_thumbnails(self, product: dict, hook_texts: list[str], styles: list[str] | None = None, progress_callback=None) -> list[dict]:
        return [{"image": b"thumb", "hook_text": hook_texts[0], "style": "dramatic"}]


class MockYouTubeClient:
    def search(self, query: str, max_results: int = 3) -> list[dict]:
        return [{"id": "vid1"}]

    def collect_video_data(self, product: dict, max_results: int = 5, include_comments: bool = True) -> dict:
        return {
            "videos": [
                {
                    "id": "vid1",
                    "comments": [{"author": "a", "text": "좋아요", "likes": 5}],
                }
            ],
            "pain_points": [{"text": "pain"}],
            "gain_points": [{"text": "gain"}],
        }

    def get_video_details(self, video_id: str) -> dict | None:
        return {"id": video_id}

    def get_video_comments(self, video_id: str, max_results: int = 20) -> list[dict]:
        return [{"text": "comment"}]

    def get_transcript(self, video_id: str) -> str | None:
        return "transcript"

    def extract_pain_points(self, comments: list[dict]) -> list[dict]:
        return [{"text": "pain"}]

    def extract_gain_points(self, comments: list[dict]) -> list[dict]:
        return [{"text": "gain"}]


class MockNaverClient:
    def search_shopping(self, query: str, max_results: int = 10) -> list[dict]:
        return [{"title": "prod"}]

    def analyze_competitors(self, products: list[dict]) -> dict:
        return {"min_price": 1000, "max_price": 2000, "avg_price": 1500}

    def search_blog(self, query: str, max_results: int = 10) -> list[dict]:
        return [{"title": "blog"}]

    def search_news(self, query: str, max_results: int = 10) -> list[dict]:
        return [{"title": "news"}]


class MockStorageService:
    def __init__(self) -> None:
        self.uploaded: list[dict[str, Any]] = []

    def health_check(self) -> bool:
        return True

    def upload(self, data, path: str, content_type: str) -> None:
        self.uploaded.append({"path": path, "content_type": content_type})

    def get_signed_url(self, path: str) -> str:
        return f"https://example.com/{path}"


class MockPipelineOrchestrator:
    async def run_pipeline(self, comments: list[dict]) -> dict[str, Any]:
        return {"insights": [{"content": "insight"}], "stats": {"total": len(comments)}}


class MockSocialMediaService:
    async def generate_posts(self, product: dict, strategy: dict, top_insights: list[dict] | None = None, platforms: list[str] | None = None) -> dict[str, Any]:
        return {"instagram": "post"}


class MockThumbnailService:
    def generate(self, product: dict, hook_text: str, style: str = "dramatic", include_text_overlay: bool = False, progress_callback=None) -> bytes | None:
        return b"thumb"

    def generate_from_strategy(self, product: dict, strategy: dict, count: int = 3, styles: list[str] | None = None, progress_callback=None) -> list[dict]:
        return [{"image": b"thumb", "style": "dramatic"}]


class MockVideoService:
    def generate_marketing_video(self, product: dict, strategy: dict, duration_seconds: int = 8, mode: str = "single", phase2_prompt: str | None = None, enable_dual_phase_beta: bool = False) -> bytes | str:
        return b"video"


class MockHistoryService:
    def save_result(self, result) -> str:
        return "saved.json"


@pytest.fixture()
def sample_product() -> dict[str, Any]:
    return {
        "name": "벅스델타",
        "category": "해충방제",
        "description": "샘플 제품",
        "target": "모든 해충",
    }


@pytest.fixture()
def mock_gemini_client() -> MockGeminiClient:
    return MockGeminiClient()


@pytest.fixture()
def mock_gemini_client_error() -> MockGeminiClient:
    return MockGeminiClient(error_mode=True)


@pytest.fixture()
def mock_youtube_client() -> MockYouTubeClient:
    return MockYouTubeClient()


@pytest.fixture()
def mock_naver_client() -> MockNaverClient:
    return MockNaverClient()


@pytest.fixture()
def mock_storage_service() -> MockStorageService:
    return MockStorageService()


@pytest.fixture()
def mock_pipeline_orchestrator() -> MockPipelineOrchestrator:
    return MockPipelineOrchestrator()


@pytest.fixture()
def mock_social_service() -> MockSocialMediaService:
    return MockSocialMediaService()


@pytest.fixture()
def mock_thumbnail_service() -> MockThumbnailService:
    return MockThumbnailService()


@pytest.fixture()
def mock_video_service() -> MockVideoService:
    return MockVideoService()


@pytest.fixture()
def mock_history_service() -> MockHistoryService:
    return MockHistoryService()
