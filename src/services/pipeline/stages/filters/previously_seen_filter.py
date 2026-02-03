from typing import List, Iterable

from services.pipeline.types import Candidate


class PreviouslySeenFilter:
    """이미 본 콘텐츠 제거"""

    def __init__(self, seen_ids: Iterable[str] | None = None):
        self.seen_ids = {i for i in (seen_ids or []) if i}

    def filter(self, candidates: List[Candidate]) -> List[Candidate]:
        if not self.seen_ids:
            return candidates
        return [c for c in candidates if c.id not in self.seen_ids]
