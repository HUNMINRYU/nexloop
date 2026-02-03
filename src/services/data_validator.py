"""
데이터 품질 검증 로직
"""

from typing import List
import re

from pydantic import BaseModel, Field, field_validator


class ValidatedComment(BaseModel):
    """검증된 댓글 데이터 모델"""

    author: str = Field(..., min_length=1)
    text: str = Field(..., min_length=5)
    likes: int = Field(0, ge=0)

    @field_validator("text")
    @classmethod
    def clean_text(cls, value: str) -> str:
        spam_patterns = [r"http[s]?://", r"카톡|텔레그램|연락주세요"]
        for pattern in spam_patterns:
            if re.search(pattern, value, re.IGNORECASE):
                raise ValueError("스팸 댓글 필터링됨")
        return value.strip()


class DataQualityReport(BaseModel):
    """데이터 품질 보고서"""

    total_count: int
    valid_count: int
    rejected_count: int
    quality_score: float


def validate_comments(
    raw_comments: List[dict],
) -> tuple[List[ValidatedComment], DataQualityReport]:
    valid: List[ValidatedComment] = []
    rejected = 0
    for comment in raw_comments:
        try:
            valid.append(ValidatedComment(**comment))
        except Exception:
            rejected += 1

    total = len(raw_comments)
    report = DataQualityReport(
        total_count=total,
        valid_count=len(valid),
        rejected_count=rejected,
        quality_score=len(valid) / max(total, 1),
    )
    return valid, report
