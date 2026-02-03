from typing import Any, Dict, List

from services.pipeline.stages.filter import QualityFilter
from services.pipeline.stages.hydration import FeatureHydrator
from services.pipeline.stages.scorer import EngagementScorer
from services.pipeline.stages.selector import TopInsightSelector
from services.pipeline.stages.source import CommentSource


class PipelineOrchestrator:
    """
    X-Algorithm Pipeine Controller (Home Mixer)
    Source -> Hydration -> Filter -> Scorer -> Selector 흐름 제어
    """

    def __init__(
        self,
        source: CommentSource,
        hydrator: FeatureHydrator,
        quality_filter: QualityFilter,
        scorer: EngagementScorer,
        selector: TopInsightSelector,
    ):
        self.source = source
        self.hydrator = hydrator
        self.filter = quality_filter
        self.scorer = scorer
        self.selector = selector

    async def run_pipeline(self, raw_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        # 1. Source: Raw Data -> Candidate 변환
        candidates = self.source.item_to_candidate(raw_data)
        original_count = len(candidates)

        # 2. Hydration: Feature Extraction (LLM) - 가장 비용이 비쌈
        # 비용 최적화를 위해 Filter를 먼저 할 수도 있지만,
        # X 철학(Rich Feature based Filtering)을 위해 Hydration 후 Filtering도 고려 가능.
        # 여기선 '가벼운 필터' -> 'Hydration' -> '무거운 필터(Scoring)' 효율적.

        # 2.1 Pre-Hydration Filter (명백한 스팸 제거로 LLM 비용 절감)
        candidates = self.filter.filter(candidates)
        filtered_count = len(candidates)

        if not candidates:
            return {
                "insights": [],
                "stats": {
                    "original_count": original_count,
                    "filtered_count": 0,
                    "processed_count": 0,
                },
            }

        # 2.2 Candidate Hydration (LLM)
        candidates = await self.hydrator.hydrate(candidates)

        # 2.3 Post-Hydration Filter (toxicity 임계치에 의해 제한)
        candidates = self.filter.filter(candidates)
        post_filtered_count = len(candidates)

        if not candidates:
            return {
                "insights": [],
                "stats": {
                    "original_count": original_count,
                    "filtered_count": filtered_count,
                    "post_filtered_count": 0,
                    "processed_count": 0,
                },
            }

        # 3. Scorer: Weighting & Ranking
        ranked_candidates = self.scorer.score(candidates)

        # 4. Selection: Top K 선정 및 포맷팅
        final_result = self.selector.select(ranked_candidates, top_k=5)

        return {
            "insights": final_result,
            "stats": {
                "original_count": original_count,
                "filtered_count": filtered_count,
                "post_filtered_count": post_filtered_count,
                "processed_count": len(ranked_candidates),
            },
        }
