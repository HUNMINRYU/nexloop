from typing import Dict, List

from services.pipeline.types import Candidate


class AuthorDiversityScorer:
    """
    동일 작성자 반복 등장 시 점수 감쇠로 피드 다양성 확보
    """

    DECAY_FACTOR = 0.7

    def apply(self, candidates: List[Candidate]) -> List[Candidate]:
        author_counts: Dict[str, int] = {}

        for candidate in candidates:
            author = candidate.author.username
            count = author_counts.get(author, 0)

            if count > 0:
                decay = self.DECAY_FACTOR ** count
                candidate.score.final_score *= decay
                candidate.score.weighted_components["diversity_decay"] = decay

            author_counts[author] = count + 1

        return sorted(candidates, key=lambda c: c.score.final_score, reverse=True)
