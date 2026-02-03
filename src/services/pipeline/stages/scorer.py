from typing import List

from services.pipeline.types import Candidate, CandidateScore


class EngagementScorer:
    """
    X-Algorithm의 Weighted Scoring 로직 구현
    Formula: Final Score = Σ (weight_i × P(action_i))
    """

    # 가중치 설정 (Implementation Plan 기준)
    WEIGHTS = {
        "purchase_intent": 10.0,
        "constructive_feedback": 5.0,
        "reply_inducing": 3.0,
        "share_probability": 8.0,
        "viral_potential": 7.0,
        "actionable_insight": 6.0,
        "quote_worthy": 4.0,
        "save_worthy": 5.0,
        "follow_author": 4.0,
        "dwell_time": 2.0,
        "toxicity": -100.0,
        "controversy_score": -2.0,
        "not_interested": -5.0,
        "report_probability": -50.0,
    }

    def score(self, candidates: List[Candidate]) -> List[Candidate]:
        for candidate in candidates:
            self._calculate_single_candidate(candidate)

        # 점수 내림차순 정렬 (Ranking)
        return sorted(candidates, key=lambda c: c.score.final_score, reverse=True)

    def _calculate_single_candidate(self, candidate: Candidate) -> None:
        features = candidate.features
        score_components = {}
        total_score = 0.0
        reasons = []

        # 1. Feature 기반 가중치 합산
        feature_dict = {
            "purchase_intent": features.purchase_intent,
            "constructive_feedback": features.constructive_feedback,
            "reply_inducing": features.reply_inducing,
            "share_probability": features.share_probability,
            "viral_potential": features.viral_potential,
            "actionable_insight": features.actionable_insight,
            "quote_worthy": features.quote_worthy,
            "save_worthy": features.save_worthy,
            "follow_author": features.follow_author,
            "dwell_time": features.dwell_time,
            "toxicity": features.toxicity,
            "controversy_score": features.controversy_score,
            "not_interested": features.not_interested,
            "report_probability": features.report_probability,
        }

        for feature_name, probability in feature_dict.items():
            weight = self.WEIGHTS.get(feature_name, 0.0)
            if weight == 0 or probability == 0:
                continue

            component_score = weight * probability
            score_components[feature_name] = component_score
            total_score += component_score

            # 설명 생성용 (Top factor만)
            if abs(component_score) > 2.0:
                effect = "높여" if component_score > 0 else "낮춰"
                reasons.append(f"{feature_name}({probability:.1f})가 점수를 {effect}줌")

        # 2. Base Metadata 가중치 (좋아요 수 등) - Log Scale 적용 추천하지만 일단 선형
        # X-Algorithml에서도 User interaction은 강력한 시그널
        engagement_boost = min(candidate.like_count * 0.1, 5.0)  # 최대 5점까지 보너스
        if engagement_boost > 0:
            total_score += engagement_boost
            score_components["engagement_boost"] = engagement_boost

        candidate.score = CandidateScore(
            final_score=round(total_score, 2),
            weighted_components=score_components,
            explanation=", ".join(reasons) if reasons else "일반적인 댓글",
        )
