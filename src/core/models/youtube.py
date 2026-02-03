"""
YouTube 관련 도메인 모델
"""
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class YouTubeComment(BaseModel):
    """YouTube 댓글 모델"""

    text: str = Field(..., description="댓글 내용")
    likes: int = Field(default=0, ge=0, description="좋아요 수")
    author: str = Field(default="", description="작성자")
    published_at: Optional[datetime] = Field(default=None, description="작성일")


class PainPoint(BaseModel):
    """고객 불만/고충 포인트"""

    text: str = Field(..., description="불만 내용")
    keyword: str = Field(..., description="핵심 키워드")
    likes: int = Field(default=0, ge=0, description="공감 수")


class GainPoint(BaseModel):
    """고객 긍정적 피드백"""

    text: str = Field(..., description="긍정적 피드백 내용")
    keyword: str = Field(..., description="핵심 키워드")
    likes: int = Field(default=0, ge=0, description="공감 수")


class YouTubeVideo(BaseModel):
    """YouTube 비디오 모델"""

    model_config = ConfigDict(populate_by_name=True)

    video_id: str = Field(..., alias="id", description="비디오 ID")
    title: str = Field(..., description="제목")
    description: str = Field(default="", description="설명")
    thumbnail_url: Optional[str] = Field(default=None, alias="thumbnail", description="썸네일 URL")
    channel: str = Field(default="", description="채널명")
    published_at: Optional[datetime] = Field(default=None, description="게시일")
    view_count: int = Field(default=0, ge=0, description="조회수")
    like_count: int = Field(default=0, ge=0, description="좋아요 수")
    comment_count: int = Field(default=0, ge=0, description="댓글 수")
    transcript: Optional[str] = Field(default=None, description="자막 텍스트")

class YouTubeSearchResult(BaseModel):
    """YouTube 검색 결과 (분석 포함)"""

    product_name: str = Field(..., description="검색 제품명")
    query: str = Field(default="", description="검색 쿼리")
    videos: list[YouTubeVideo] = Field(default_factory=list, description="검색된 비디오 목록")
    pain_points: list[PainPoint] = Field(default_factory=list, description="추출된 페인 포인트")
    gain_points: list[GainPoint] = Field(default_factory=list, description="추출된 게인 포인트")
    total_comments_analyzed: int = Field(default=0, ge=0, description="분석된 총 댓글 수")
    collected_at: datetime = Field(default_factory=datetime.now, description="수집 시간")

    @property
    def video_count(self) -> int:
        """비디오 수"""
        return len(self.videos)
