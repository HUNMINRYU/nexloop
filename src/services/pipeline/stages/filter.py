from typing import List, Iterable

from config.settings import get_settings

from services.pipeline.types import Candidate


class QualityFilter:
    """
    X-Algorithm의 Pre-Scoring Filtering 단계
    스팸, 중복, 저품질 콘텐츠를 사전에 제거하여 Scoring 연산 낭비 방지
    """

    MIN_LENGTH = 5
    SPAM_KEYWORDS = ["광고", "홍보", "http", "카톡", "사다리", "토토"]

    def __init__(self, custom_banned_keywords: Iterable[str] | None = None) -> None:
        if custom_banned_keywords is None:
            custom_banned_keywords = get_settings().brand_banned_keywords
        self._custom_banned_keywords = [
            keyword.strip() for keyword in custom_banned_keywords if keyword.strip()
        ]

    def filter(self, candidates: List[Candidate]) -> List[Candidate]:
        filtered_candidates = []
        for candidate in candidates:
            if self._is_eligible(candidate):
                filtered_candidates.append(candidate)
        return filtered_candidates

    def _is_eligible(self, candidate: Candidate) -> bool:
        # 1. 길이 필터
        if len(candidate.content.strip()) < self.MIN_LENGTH:
            return False

        # 2. 스팸 키워드 필터
        for keyword in self.SPAM_KEYWORDS:
            if keyword in candidate.content:
                return False

        # 2-1. 커스텀 금지어 필터
        for keyword in self._custom_banned_keywords:
            if keyword in candidate.content:
                return False

        # 3. Toxicity 필터 (이미 Feature가 있다면)
        if candidate.features.toxicity > 0.8:
            return False

        return True
