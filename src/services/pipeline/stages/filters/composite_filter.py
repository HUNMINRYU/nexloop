from typing import List

from services.pipeline.types import Candidate
from services.pipeline.stages.query_hydrator import UserContext
from .age_filter import AgeFilter
from .author_block_filter import AuthorBlockFilter
from .duplicate_filter import DuplicateFilter
from .muted_keyword_filter import MutedKeywordFilter
from .previously_seen_filter import PreviouslySeenFilter
from .spam_filter import SpamFilter


class CompositeFilter:
    """모든 필터 통합"""

    def __init__(self) -> None:
        self._duplicate = DuplicateFilter()
        self._age = AgeFilter()
        self._spam = SpamFilter()

    def filter(self, candidates: List[Candidate], user_context: UserContext | None = None) -> List[Candidate]:
        filtered = self._duplicate.filter(candidates)
        filtered = self._age.filter(filtered)
        filtered = self._spam.filter(filtered)

        if user_context:
            filtered = MutedKeywordFilter(set(user_context.muted_keywords)).filter(filtered)
            filtered = AuthorBlockFilter(user_context.blocked_authors).filter(filtered)
            filtered = PreviouslySeenFilter(user_context.engagement_history).filter(filtered)

        return filtered
