"""
YouTube 서비스
YouTube 데이터 수집 비즈니스 로직
"""

from typing import Callable, Optional

from core.exceptions import DataCollectionError
from core.interfaces.api_client import IYouTubeClient
from utils.cache import cached
from utils.logger import (
    log_api_end,
    log_api_start,
    log_data,
    log_error,
    log_step,
    log_success,
)
from utils.retry import retry_on_error


class YouTubeService:
    """YouTube 데이터 수집 서비스"""

    def __init__(self, client: IYouTubeClient) -> None:
        self._client = client

    @cached(ttl=600, cache_key_prefix="youtube")  # 10분 캐시
    @retry_on_error(max_attempts=3, base_delay=1.0, max_delay=8.0)
    def search_videos(self, query: str, max_results: int = 3) -> list[dict]:
        """비디오 검색 (캐시 적용: 동일 검색어는 10분간 재사용)"""
        log_api_start("YouTube Search", f"Query: {query}, Max: {max_results}")

        try:
            results = self._client.search(query, max_results)
            log_api_end("YouTube Search", items=len(results))
            return results
        except Exception as e:
            log_error(f"YouTube 검색 실패: {e}")
            raise DataCollectionError(
                "YouTube 검색 실패",
                original_error=e,
            )

    def get_video_details(self, video_id: str) -> dict | None:
        """비디오 상세 정보"""
        return self._client.get_video_details(video_id)

    def get_comments(self, video_id: str, max_results: int = 20) -> list[dict]:
        """비디오 댓글"""
        return self._client.get_video_comments(video_id, max_results)

    def get_transcript(self, video_id: str) -> str | None:
        """비디오 자막"""
        return self._client.get_transcript(video_id)

    @retry_on_error(max_attempts=3, base_delay=1.0, max_delay=8.0)
    def collect_product_data(
        self,
        product: dict,
        max_results: int = 5,
        include_comments: bool = True,
        progress_callback: Optional[Callable[[str, int], None]] = None,
    ) -> dict:
        """제품 기반 YouTube 데이터 수집"""
        p_name = product.get("name", "N/A")
        log_step(
            "YouTube 데이터 수집",
            "시작",
            f"제품: {p_name}, 댓글포함: {include_comments}",
        )

        try:
            if progress_callback:
                progress_callback("YouTube 데이터 수집 중...", 10)

            data = self._client.collect_video_data(
                product=product,
                max_results=max_results,
                include_comments=include_comments,
            )

            if progress_callback:
                progress_callback("YouTube 데이터 수집 완료", 100)

            video_count = len(data.get("videos", []))
            log_success(f"YouTube 데이터 수집 완료 ({video_count}개)")
            log_data("Videos", video_count, "YouTube")

            return data

        except Exception as e:
            log_error(f"YouTube 데이터 수집 실패: {e}")
            raise DataCollectionError(
                f"YouTube 데이터 수집 실패: {e}",
                original_error=e,
            )

    def analyze_comments(self, comments: list[dict]) -> dict:
        """댓글 분석 (페인/게인 포인트)"""
        pain_points = self._client.extract_pain_points(comments)
        gain_points = self._client.extract_gain_points(comments)

        return {
            "total_comments": len(comments),
            "pain_points": pain_points,
            "gain_points": gain_points,
            "pain_count": len(pain_points),
            "gain_count": len(gain_points),
        }
