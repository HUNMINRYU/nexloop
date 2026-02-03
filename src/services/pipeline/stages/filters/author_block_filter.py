from typing import List, Iterable

from services.pipeline.types import Candidate


class AuthorBlockFilter:
    """차단된 작성자 제거"""

    def __init__(self, blocked_authors: Iterable[str] | None = None):
        self.blocked_authors = {a for a in (blocked_authors or []) if a}

    def filter(self, candidates: List[Candidate]) -> List[Candidate]:
        if not self.blocked_authors:
            return candidates
        return [
            c for c in candidates if c.author.username not in self.blocked_authors
        ]
