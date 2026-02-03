"""
마케팅 전략 관련 도메인 모델
"""
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, field_serializer


class TargetPersona(BaseModel):
    """타겟 고객 페르소나"""

    primary: str = Field(..., description="주요 타겟 고객층")
    secondary: str = Field(default="", description="2차 타겟 고객층")
    age_range: str = Field(default="", description="연령대")
    pain_points: list[str] = Field(default_factory=list, description="고객 페인 포인트")
    desires: list[str] = Field(default_factory=list, description="고객이 원하는 것")


class HookingPoint(BaseModel):
    """바이럴 훅 포인트"""

    hook: str = Field(..., description="훅 텍스트")
    hook_type: str = Field(..., description="훅 유형 (loss_aversion, social_proof 등)")
    viral_score: int = Field(default=0, ge=0, le=100, description="바이럴 점수")
    explanation: Optional[str] = Field(default=None, description="효과 설명")


class ShortformScenario(BaseModel):
    """숏폼 비디오 시나리오"""

    title: str = Field(..., description="시나리오 제목")
    scenario_type: str = Field(..., description="시나리오 유형")
    thumbnail_text: str = Field(..., description="썸네일 텍스트")
    script: str = Field(..., description="스크립트 내용")
    duration_seconds: int = Field(default=15, ge=5, le=60, description="예상 길이(초)")


class SNSCopy(BaseModel):
    """SNS 플랫폼별 마케팅 카피"""

    instagram: Optional[str] = Field(default=None, description="인스타그램용 카피")
    youtube_shorts: Optional[str] = Field(default=None, description="유튜브 쇼츠용 카피")
    tiktok: Optional[str] = Field(default=None, description="틱톡용 카피")
    facebook: Optional[str] = Field(default=None, description="페이스북용 카피")


class CompetitorAnalysis(BaseModel):
    """경쟁사 분석 결과"""

    price_range: str = Field(default="", description="가격대 분석")
    key_features: list[str] = Field(default_factory=list, description="주요 경쟁 기능")
    differentiators: list[str] = Field(default_factory=list, description="차별화 포인트")
    weaknesses: list[str] = Field(default_factory=list, description="경쟁사 약점")


class ContentStrategy(BaseModel):
    """콘텐츠 전략"""

    trending_topics: list[str] = Field(default_factory=list, description="인기 주제")
    content_types: list[str] = Field(default_factory=list, description="효과적인 콘텐츠 유형")
    posting_tips: list[str] = Field(default_factory=list, description="포스팅 팁")
    recommended_hashtags: list[str] = Field(default_factory=list, description="추천 해시태그")


class MarketTrend(BaseModel):
    """시장 트렌드 요약"""

    title: str = Field(default="", description="이슈 제목")
    summary: str = Field(default="", description="이슈 요약")
    url: str = Field(default="", description="출처 링크")


class MarketingStrategy(BaseModel):
    """완전한 마케팅 전략 출력"""

    model_config = ConfigDict()

    product_name: str = Field(..., description="제품명")
    target_persona: Optional[TargetPersona] = Field(default=None, description="타겟 페르소나")
    hooking_points: list[HookingPoint] = Field(default_factory=list, description="훅 포인트 목록")
    shortform_scenarios: list[ShortformScenario] = Field(default_factory=list, description="숏폼 시나리오")
    sns_copies: Optional[SNSCopy] = Field(default=None, description="SNS 카피")
    competitor_analysis: Optional[CompetitorAnalysis] = Field(default=None, description="경쟁사 분석")
    content_strategy: Optional[ContentStrategy] = Field(default=None, description="콘텐츠 전략")
    market_trends: list[MarketTrend] = Field(default_factory=list, description="시장 트렌드")
    video_prompt: Optional[str] = Field(default=None, description="비디오 생성 프롬프트")
    keywords: list[str] = Field(default_factory=list, description="핵심 키워드")
    summary: str = Field(default="", description="전체 분석 요약")
    generated_at: datetime = Field(default_factory=datetime.now, description="생성 시간")

    @field_serializer("generated_at")
    def serialize_generated_at(self, value: datetime) -> str:
        return value.isoformat()
