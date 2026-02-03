"""
데이터 수집 서비스
YouTube + Naver + X-Algorithm 인사이트 수집
"""

import asyncio
import threading
from typing import Callable, Optional

from core.models import CollectedData, PipelineConfig, PipelineStep
from services.data_validator import validate_comments
from services.market_trend_service import MarketTrendService
from services.naver_service import NaverService
from services.pipeline.orchestrator import PipelineOrchestrator
from services.youtube_service import YouTubeService
from utils.logger import get_logger, log_error, log_info, log_step

logger = get_logger(__name__)


class DataCollectionService:
    """데이터 수집 통합 서비스"""

    def __init__(
        self,
        youtube_service: YouTubeService,
        naver_service: NaverService,
        pipeline_orchestrator: PipelineOrchestrator,
        market_trend_service: MarketTrendService | None = None,
    ) -> None:
        self._youtube = youtube_service
        self._naver = naver_service
        self._orchestrator = pipeline_orchestrator
        self._market_trend = market_trend_service

    def collect_all_data(
        self,
        product: dict,
        config: PipelineConfig,
        progress_callback: Optional[Callable[[PipelineStep, str], None]] = None,
    ) -> CollectedData:
        """전체 데이터 수집"""
        p_name = product.get("name", "N/A")
        log_step("데이터 수집", "시작", f"제품: {p_name}")

        collected_data = CollectedData()

        if progress_callback:
            progress_callback(PipelineStep.YOUTUBE_COLLECTION, "YouTube 데이터 수집 중...")

        youtube_data = self._youtube.collect_product_data(
            product=product,
            max_results=config.youtube_count,
            include_comments=config.include_comments,
        )
        collected_data.youtube_data = youtube_data
        collected_data.pain_points = youtube_data.get("pain_points", [])
        collected_data.gain_points = youtube_data.get("gain_points", [])

        if progress_callback:
            progress_callback(PipelineStep.NAVER_COLLECTION, "네이버 쇼핑 데이터 수집 중...")

        naver_data = self._naver.collect_product_data(
            product=product,
            max_results=config.naver_count,
        )
        collected_data.naver_data = naver_data

        if self._market_trend:
            if progress_callback:
                progress_callback(PipelineStep.DATA_COLLECTION, "시장 동향 수집 중...")
            collected_data.market_trends = self._market_trend.get_market_trends(product)

        if progress_callback:
            progress_callback(PipelineStep.COMMENT_ANALYSIS, "X-Algorithm 인사이트 분석 중...")

        try:
            comments = []
            if youtube_data and "videos" in youtube_data:
                for v in youtube_data["videos"]:
                    for c in v.get("comments", []):
                        comments.append(
                            {
                                "author": c.get("author", "unknown"),
                                "text": c.get("text", ""),
                                "likes": c.get("likes", 0),
                            }
                        )

            if not comments and youtube_data:
                for c in youtube_data.get("top_comments", []):
                    comments.append(
                        {
                            "author": c.get("author", "unknown"),
                            "text": c.get("text", ""),
                            "likes": c.get("likes", 0),
                        }
                    )

            seen_texts = set()
            unique_comments = []
            for c in comments:
                text = c.get("text", "").strip()
                if not text or text in seen_texts:
                    continue
                seen_texts.add(text)
                unique_comments.append(c)

            unique_comments.sort(key=lambda x: x.get("likes", 0), reverse=True)
            limited_comments = unique_comments[: config.max_comment_samples]

            log_info(
                f"X-Algorithm 댓글 샘플링: {len(limited_comments)}/{len(unique_comments)}"
            )

            validated, quality_report = validate_comments(limited_comments)
            collected_data.quality_report = quality_report.model_dump()
            log_info(
                f"데이터 품질: {quality_report.quality_score:.1%} "
                f"({quality_report.valid_count}/{quality_report.total_count})"
            )

            validated_payload = [item.model_dump() for item in validated]
            analysis_result = self._run_async(
                self._orchestrator.run_pipeline(validated_payload)
            )
            collected_data.top_insights = analysis_result.get("insights", [])
            log_info(f"X-Algorithm 분석 완료: {len(collected_data.top_insights)}개 인사이트 도출")
        except Exception as e:
            logger.error(f"X-Algorithm 분석 실패: {e}")
            log_error(f"X-Algorithm 분석 중 오류 발생: {e}")

        if progress_callback:
            progress_callback(PipelineStep.DATA_COLLECTION, "데이터 수집 완료")

        return collected_data

    @staticmethod
    def _run_async(coro):
        """새 이벤트 루프에서 비동기 작업 실행"""
        try:
            running_loop = asyncio.get_running_loop()
        except RuntimeError:
            running_loop = None

        if running_loop is None:
            loop = asyncio.new_event_loop()
            try:
                asyncio.set_event_loop(loop)
                return loop.run_until_complete(coro)
            finally:
                loop.close()

        result_container: dict[str, object] = {}
        error_container: dict[str, BaseException] = {}

        def runner():
            loop = asyncio.new_event_loop()
            try:
                asyncio.set_event_loop(loop)
                result_container["result"] = loop.run_until_complete(coro)
            except BaseException as exc:
                error_container["error"] = exc
            finally:
                loop.close()

        thread = threading.Thread(target=runner, daemon=True)
        thread.start()
        thread.join()

        if "error" in error_container:
            raise error_container["error"]

        return result_container.get("result")
