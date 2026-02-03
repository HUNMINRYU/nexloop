"""
Social Media Post Generation Service
채널별(인스타그램, 트위터, 블로그 등) 마케팅 문구 생성
"""
from typing import Any

from core.interfaces.ai_service import IMarketingAIService
from core.prompts import prompt_registry
from core.prompts import social_media_prompts  # noqa: F401
from api import validate_json_output
from utils.logger import get_logger, log_llm_fail, log_llm_request, log_llm_response, log_step, log_success

logger = get_logger(__name__)

class SocialMediaService:
    def __init__(self, gemini_client: IMarketingAIService):
        self._gemini = gemini_client

    async def generate_posts(
        self,
        product: dict,
        strategy: dict,
        top_insights: list[dict] = None,
        platforms: list[str] = None,
    ) -> dict[str, Any]:
        if not platforms:
            platforms = ["instagram", "twitter", "blog"]

        log_step("SNS 포스팅 생성", "시작", f"플랫폼: {platforms}")

        product_name = product.get("name", "제품")
        summary = strategy.get("summary", "")

        import json
        insights_text = (
            json.dumps(top_insights, ensure_ascii=False, indent=2)
            if top_insights
            else "N/A"
        )

        prompt = prompt_registry.get("social.media.posts").render(
            product_name=product_name,
            summary=summary,
            insights_text=insights_text,
        )
        log_llm_request("SNS 포스팅 생성", f"제품: {product_name}, 플랫폼: {platforms}")
        try:
            # 인터페이스 타입 힌트에도 불구하고 실제 인스턴스가 generate_content_async를 가지고 있는지 확인
            if hasattr(self._gemini, "generate_content_async"):
                response_text = await self._gemini.generate_content_async(prompt)
            else:
                # 동기 방식 fallback (테스트용)
                response_text = self._gemini.generate_text(prompt)

            if not response_text or not response_text.strip():
                raise ValueError("빈 응답을 수신했습니다.")

            result = validate_json_output(
                response_text,
                required_fields=["instagram", "twitter", "blog"],
            )

            if "error" in result:
                raise ValueError(result.get("error"))

            log_llm_response("SNS 포스팅 생성", f"응답 {len(response_text)}자")
            log_success("SNS 포스팅 생성 완료")
            return result
        except Exception as e:
            log_llm_fail("SNS 포스팅 생성", str(e))
            logger.error(f"SNS 포스팅 생성 실패: {e}")
            return {
                "error": str(e),
                "instagram": {"caption": "생성 실패", "hashtags": []},
                "twitter": {"content": "생성 실패"},
                "blog": {"title": "생성 실패", "content": "생성 실패"}
            }
