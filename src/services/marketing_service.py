"""
마케팅 서비스
AI 기반 마케팅 전략 생성 비즈니스 로직
"""

from typing import Any, Callable, Optional

from core.exceptions import StrategyGenerationError
from core.interfaces.ai_service import IMarketingAIService
from core.models import CollectedData
from utils.logger import (
    log_api_end,
    log_api_start,
    log_error,
    log_step,
    log_success,
)


class MarketingService:
    """마케팅 전략 생성 서비스"""

    def __init__(self, client: IMarketingAIService) -> None:
        self._client = client

    def analyze_data(
        self,
        youtube_data: dict,
        naver_data: dict,
        product_name: str,
        top_insights: list[dict] = None,
        market_trends: dict | None = None,
        progress_callback: Optional[Callable[[str, int], None]] = None,
        use_grounding: bool = True,
    ) -> dict[str, Any]:
        """마케팅 데이터 분석"""
        log_step(
            "마케팅 데이터 분석",
            "시작",
            f"제품: {product_name}, Grounding: {use_grounding}",
        )
        log_api_start("Gemini Analysis", f"Product: {product_name}")

        try:
            result = self._client.analyze_marketing_data(
                youtube_data=youtube_data,
                naver_data=naver_data,
                product_name=product_name,
                top_insights=top_insights,
                market_trends=market_trends,
                progress_callback=progress_callback,
                use_search_grounding=use_grounding,
            )

            if "error" in result:
                raise StrategyGenerationError(result["error"])

            log_api_end("Gemini Analysis")
            log_success("마케팅 데이터 분석 완료")
            return result

        except StrategyGenerationError:
            raise
        except Exception as e:
            log_error(f"마케팅 데이터 분석 실패: {e}")
            raise StrategyGenerationError(
                f"마케팅 데이터 분석 실패: {e}",
                original_error=e,
            )

    def generate_strategy(
        self,
        product: dict,
        collected_data: CollectedData,
        progress_callback: Optional[Callable[[str, int], None]] = None,
    ) -> dict[str, Any]:
        """마케팅 전략 생성"""
        log_step("마케팅 전략 수립", "시작")
        log_api_start("Gemini Strategy Generation")

        try:
            result = self._client.generate_marketing_strategy(
                collected_data={
                    "product": product,
                    "youtube_data": collected_data.youtube_data or {},
                    "naver_data": collected_data.naver_data or {},
                    "top_insights": collected_data.top_insights,
                    "market_trends": collected_data.market_trends,
                },
                progress_callback=progress_callback,
            )

            if "error" in result:
                raise StrategyGenerationError(result["error"])

            log_api_end("Gemini Strategy Generation")
            log_success("마케팅 전략 생성 완료")
            return result

        except StrategyGenerationError:
            raise
        except Exception as e:
            log_error(f"마케팅 전략 생성 실패: {e}")
            raise StrategyGenerationError(
                f"마케팅 전략 생성 실패: {e}",
                original_error=e,
            )

    def generate_hooks(
        self,
        product_name: str,
        hook_types: list[str] | None = None,
        count: int = 5,
    ) -> list[dict]:
        """훅 텍스트 생성"""
        return self._client.generate_hook_texts(
            product_name=product_name,
            hook_types=hook_types,
            count=count,
        )

    def extract_key_insights(self, strategy: dict) -> dict:
        """전략에서 핵심 인사이트 추출"""
        return {
            "target_audience": strategy.get("target_audience", {}),
            "hooks": strategy.get("hook_suggestions", [])[:3],
            "keywords": strategy.get("keywords", [])[:5],
            "summary": strategy.get("summary", ""),
        }
