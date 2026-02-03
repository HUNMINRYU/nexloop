import uuid
from datetime import datetime
from typing import Any, Dict, List

from services.pipeline.types import AuthorInfo, Candidate


class CommentSource:
    """Raw Dict 데이터를 Candidate 객체로 변환 (Thunder 역할)"""

    def item_to_candidate(self, raw_items: List[Dict[str, Any]]) -> List[Candidate]:
        candidates = []
        for item in raw_items:
            author_name = item.get("author", "Anonymous")
            text = item.get("text", "")
            likes = (
                int(item.get("likes", 0))
                if str(item.get("likes", "0")).isdigit()
                else 0
            )

            c_id = str(item.get("id", uuid.uuid4()))

            candidate = Candidate(
                id=c_id,
                content=text,
                author=AuthorInfo(username=author_name),
                created_at=datetime.now(),
                like_count=likes,
            )
            candidates.append(candidate)
        return candidates
