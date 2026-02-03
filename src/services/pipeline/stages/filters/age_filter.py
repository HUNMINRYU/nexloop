from datetime import datetime, timedelta
from typing import List

from services.pipeline.types import Candidate


class AgeFilter:
    """오래된 콘텐츠 제거"""

    def __init__(self, max_age_days: int = 30):
        self.max_age = timedelta(days=max_age_days)

    def filter(self, candidates: List[Candidate]) -> List[Candidate]:
        now = datetime.now()
        return [c for c in candidates if self._is_fresh(c, now)]

    def _is_fresh(self, candidate: Candidate, now: datetime) -> bool:
        if not candidate.created_at:
            return True
        return (now - candidate.created_at) < self.max_age
