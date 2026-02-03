from typing import List, Set

from services.pipeline.types import Candidate


class MutedKeywordFilter:
    """특정 키워드 포함 콘텐츠 제거"""

    DEFAULT_MUTED: Set[str] = {"광고", "홍보", "스팸", "카톡", "텔레그램", "링크"}

    def __init__(self, keywords: Set[str] | None = None):
        self.keywords = keywords or self.DEFAULT_MUTED

    def filter(self, candidates: List[Candidate]) -> List[Candidate]:
        return [c for c in candidates if not self._contains_muted(c)]

    def _contains_muted(self, candidate: Candidate) -> bool:
        text = candidate.content.lower()
        return any(kw.lower() in text for kw in self.keywords)
