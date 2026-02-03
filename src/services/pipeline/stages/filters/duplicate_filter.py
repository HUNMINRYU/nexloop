from typing import List, Set

from services.pipeline.types import Candidate


class DuplicateFilter:
    """중복 콘텐츠 제거"""

    def filter(self, candidates: List[Candidate]) -> List[Candidate]:
        seen: Set[str] = set()
        result = []
        for c in candidates:
            text = c.content.strip()
            if not text or text in seen:
                continue
            seen.add(text)
            result.append(c)
        return result
