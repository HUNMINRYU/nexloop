from typing import List, Iterable

from services.pipeline.types import Candidate


class SpamFilter:
    """스팸/광고 필터"""

    DEFAULT_KEYWORDS = ["광고", "홍보", "http", "카톡", "사다리", "토토", "링크"]

    def __init__(self, keywords: Iterable[str] | None = None):
        self.keywords = [kw.strip() for kw in (keywords or self.DEFAULT_KEYWORDS) if kw.strip()]

    def filter(self, candidates: List[Candidate]) -> List[Candidate]:
        return [c for c in candidates if not self._is_spam(c)]

    def _is_spam(self, candidate: Candidate) -> bool:
        text = candidate.content.lower()
        return any(keyword.lower() in text for keyword in self.keywords)
