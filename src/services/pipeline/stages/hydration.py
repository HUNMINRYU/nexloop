import asyncio
import hashlib
from typing import List, cast

from core.interfaces.ai_service import IMarketingAIService
from core.prompts import prompt_registry
from core.prompts import hydration_prompts  # noqa: F401
from services.pipeline.types import Candidate, CandidateFeatures
from api import validate_json_output
from utils.logger import get_logger, log_llm_fail, log_llm_request, log_llm_response
from utils.cache import TTLCache

logger = get_logger(__name__)

MAX_CONCURRENT_REQUESTS = 5
_feature_cache = TTLCache(default_ttl=86400)


class FeatureHydrator:
    """
    X-Algorithm의 Hydration 단계 (LLM Feature Extraction)
    단순 댓글 텍스트 -> Rich Feature (구매의도, 바이럴 가능성 등) 변환
    """

    def __init__(self, gemini_client: IMarketingAIService):
        self.gemini_client = gemini_client

    async def hydrate(self, candidates: List[Candidate]) -> List[Candidate]:
        """
        Gemini를 통해 댓글들의 Feature를 추출하고 채워넣음
        (비용 효율성을 위해 배치 처리 권장, 여기선 단순 Loop/Async 예시)
        """
        if not candidates:
            return []

        # 프롬프트 구성 (한 번에 여러 개 분석 가능하지만, 정밀도를 위해 개별 or 소량 배치)
        # 여기선 간단히 1:1로 구현하되, 추후 Batch 로직으로 고도화 가능
        semaphore = asyncio.Semaphore(MAX_CONCURRENT_REQUESTS)

        async def rate_limited_analyze(candidate: Candidate) -> Candidate:
            async with semaphore:
                await asyncio.sleep(0.2)
                return await self._analyze_single_comment(candidate)

        tasks = [rate_limited_analyze(c) for c in candidates]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        processed: List[Candidate] = []
        success_count = 0
        for index, result in enumerate(results):
            if isinstance(result, BaseException):
                processed.append(candidates[index])
            else:
                processed.append(cast(Candidate, result))
                success_count += 1

        logger.info(f"Hydration 완료: 성공={success_count}/{len(candidates)}")
        return processed

    async def _analyze_single_comment(self, candidate: Candidate) -> Candidate:
        cache_key = hashlib.md5(candidate.content.encode("utf-8")).hexdigest()
        cached = _feature_cache.get(cache_key)
        if cached:
            candidate.features = CandidateFeatures(**cached)
            return candidate

        # Prompt Engineering for Feature Extraction
        prompt = prompt_registry.get("hydration.feature_extraction").render(
            comment=candidate.content
        )
        log_llm_request("Hydration 피처 추출", f"댓글 {len(candidate.content)}자")

        try:
            # Gemini 호출 (시스템 인스트럭션 등은 Client 내부 설정 활용)
            response_text = await self.gemini_client.generate_content_async(prompt)

            if not response_text or not response_text.strip():
                raise ValueError("빈 응답을 수신했습니다.")

            log_llm_response("Hydration 피처 추출", f"응답 {len(response_text)}자")
            data = validate_json_output(
                response_text,
                required_fields=[
                    "purchase_intent",
                    "reply_inducing",
                    "constructive_feedback",
                    "sentiment_intensity",
                    "toxicity",
                    "keywords",
                ],
            )

            if "error" in data:
                raise ValueError(data.get("error"))

            # Feature 객체 생성 및 주입
            features = CandidateFeatures(
                purchase_intent=data.get("purchase_intent", 0.0),
                constructive_feedback=data.get("constructive_feedback", 0.0),
                reply_inducing=data.get("reply_inducing", 0.0),
                share_probability=data.get("share_probability", 0.0),
                viral_potential=data.get("viral_potential", 0.0),
                actionable_insight=data.get("actionable_insight", 0.0),
                quote_worthy=data.get("quote_worthy", 0.0),
                save_worthy=data.get("save_worthy", 0.0),
                follow_author=data.get("follow_author", 0.0),
                sentiment_intensity=data.get("sentiment_intensity", 0.0),
                dwell_time=data.get("dwell_time", 0.0),
                toxicity=data.get("toxicity", 0.0),
                controversy_score=data.get("controversy_score", 0.0),
                not_interested=data.get("not_interested", 0.0),
                report_probability=data.get("report_probability", 0.0),
                keywords=data.get("keywords", []),
                topics=data.get("topics", []),
            )
            candidate.features = features
            _feature_cache.set(
                cache_key,
                {
                    "purchase_intent": features.purchase_intent,
                    "constructive_feedback": features.constructive_feedback,
                    "reply_inducing": features.reply_inducing,
                    "share_probability": features.share_probability,
                    "viral_potential": features.viral_potential,
                    "actionable_insight": features.actionable_insight,
                    "quote_worthy": features.quote_worthy,
                    "save_worthy": features.save_worthy,
                    "follow_author": features.follow_author,
                    "sentiment_intensity": features.sentiment_intensity,
                    "dwell_time": features.dwell_time,
                    "toxicity": features.toxicity,
                    "controversy_score": features.controversy_score,
                    "not_interested": features.not_interested,
                    "report_probability": features.report_probability,
                    "keywords": features.keywords,
                    "topics": features.topics,
                },
            )

        except Exception as e:
            log_llm_fail("Hydration 피처 추출", str(e))
            logger.warning(f"Hydration 실패: comment_id={candidate.id}, error={e}")

        return candidate
