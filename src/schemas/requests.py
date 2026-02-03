from typing import Any, Literal
from pydantic import BaseModel, Field


class PipelineRequest(BaseModel):
    product_name: str
    youtube_count: int = 3
    naver_count: int = 10
    include_comments: bool = True
    generate_social: bool = True
    generate_video: bool = True
    generate_thumbnails: bool = True
    export_to_notion: bool = True
    thumbnail_count: int | None = Field(
        default=None, ge=1, le=5, description="생성할 썸네일 수"
    )
    thumbnail_styles: list[str] | None = Field(
        default=None, description="썸네일 스타일 목록"
    )


class RefreshUrlRequest(BaseModel):
    gcs_path: str = Field(..., description="GCS 경로 또는 gs:// 버킷 경로")


class HookGenerateRequest(BaseModel):
    product_name: str
    style: str = Field(..., description="심리 모델 스타일")
    count: int = Field(default=1, ge=1, le=5)


class ThumbnailCompareRequest(BaseModel):
    product_name: str
    hook_text: str = Field(
        default="",
        description="훅 문구 (비어 있으면 제품명 사용, auto_hook_per_style 시 무시)",
    )
    styles: list[str] | None = Field(
        default=None, description="비교할 스타일 key 목록, 비면 전체"
    )
    include_text_overlay: bool = Field(default=True)
    max_styles: int = Field(
        default=9,
        ge=1,
        le=20,
        description="최대 생성 개수 (styles 비었을 때, 기본 9종)",
    )
    auto_hook_per_style: bool = Field(
        default=False,
        description="True면 입력 훅 무시, 스타일별로 LLM이 훅 1개씩 생성해 각 스타일에 적용",
    )


class VideoGenerateRequest(BaseModel):
    product_name: str
    hook_text: str
    duration_seconds: int = Field(default=8, ge=5, le=30)
    resolution: str = Field(default="720p")
    camera_movement: str | None = None
    composition: str | None = None
    lighting_mood: str | None = None
    audio_preset: str | None = None
    sfx: list[str] = Field(default_factory=list)
    ambient: str | None = None


class AnalysisTaskRequest(BaseModel):
    task_id: str


class CTRPredictRequest(BaseModel):
    task_id: str
    title: str
    thumbnail_description: str = ""
    competitor_titles: list[str] = Field(default_factory=list)


class NotionExportRequest(BaseModel):
    task_id: str | None = None
    history_id: str | None = None
    parent_page_id: str | None = None


class LeadRequest(BaseModel):
    email: str


class AuthSignupRequest(BaseModel):
    email: str
    password: str
    name: str | None = None
    team_name: str | None = None
    job_title: str | None = None
    phone_number: str | None = None


class AuthLoginRequest(BaseModel):
    email: str
    password: str


class ChatRequest(BaseModel):
    message: str
    session_id: str | None = None


class ApprovalStatusRequest(BaseModel):
    status: str = Field(..., description="approval status")


class RoleCreateRequest(BaseModel):
    name: str
    description: str | None = None


class TeamCreateRequest(BaseModel):
    name: str


class ScheduleRequest(BaseModel):
    """스케줄 생성/수정 요청"""

    name: str = Field(..., min_length=1, max_length=100, description="스케줄 이름")
    description: str | None = Field(None, max_length=500, description="스케줄 설명")

    # 스케줄 설정
    frequency: Literal['daily', 'weekly', 'custom'] = Field(
        default='daily',
        description="실행 주기: daily(매일), weekly(매주), custom(사용자 정의)"
    )
    days_of_week: list[int] = Field(
        default_factory=list,
        description="요일 목록 (0=월요일, 6=일요일), 비어있으면 매일"
    )
    hour: int = Field(..., ge=0, le=23, description="실행 시간 (0-23)")
    minute: int = Field(..., ge=0, le=59, description="실행 분 (0-59)")
    timezone: str = Field(default="Asia/Seoul", description="타임존")

    # 파이프라인 설정
    product_name: str = Field(..., description="실행할 제품명")
    pipeline_config: PipelineRequest = Field(..., description="파이프라인 설정")

class InsightMetrics(BaseModel):
    impressions: int | None = Field(default=None, ge=0)
    clicks: int | None = Field(default=None, ge=0)
    ctr: float | None = Field(default=None, ge=0)
    cvr: float | None = Field(default=None, ge=0)
    spend: float | None = Field(default=None, ge=0)
    roi: float | None = None


class InsightUploadItem(BaseModel):
    title: str = Field(..., min_length=1)
    content: str = Field(..., min_length=1)
    doc_type: Literal[
        "internal_upload",
        "trend_search",
        "social_trend",
        "news_summary",
        "daily_report",
    ] = "internal_upload"
    source: str | None = None
    campaign_name: str | None = None
    channel: str | None = None
    region: str | None = None
    period_start: str | None = None
    period_end: str | None = None
    metrics: InsightMetrics | None = None
    tags: list[str] = Field(default_factory=list)


class InsightUploadRequest(BaseModel):
    items: list[InsightUploadItem]

class NaverInsightBatchRequest(BaseModel):
    query: str = Field(..., min_length=1)
    max_results: int = Field(default=10, ge=1, le=50)
    include_products: bool = True
    include_blogs: bool = True
    include_news: bool = True
    campaign_name: str | None = None
    channel: str | None = None
    region: str | None = None
    period_start: str | None = None
    period_end: str | None = None

class DailyReportRequest(BaseModel):
    query: str = Field(..., min_length=1)
    max_results: int = Field(default=50, ge=1, le=50)
    doc_type: str | None = None
    campaign_name: str | None = None
    channel: str | None = None
    region: str | None = None
    period_start: str | None = None
    period_end: str | None = None
    title: str | None = None
