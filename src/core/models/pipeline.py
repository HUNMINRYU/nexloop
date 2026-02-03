"""
파이프라인 실행 관련 도메인 모델
"""
from datetime import datetime
from enum import Enum
from typing import Any, ClassVar, Optional, Tuple

from pydantic import BaseModel, ConfigDict, Field, PrivateAttr


class PipelineStep(str, Enum):
    """파이프라인 실행 단계"""

    INITIALIZED = "initialized"
    DATA_COLLECTION = "data_collection"
    YOUTUBE_COLLECTION = "youtube_collection"
    NAVER_COLLECTION = "naver_collection"
    COMMENT_ANALYSIS = "comment_analysis"
    STRATEGY_GENERATION = "strategy_generation"
    SOCIAL_GENERATION = "social_generation"
    THUMBNAIL_CREATION = "thumbnail_creation"
    VIDEO_GENERATION = "video_generation"
    UPLOAD = "upload"
    COMPLETED = "completed"
    FAILED = "failed"


class UploadStatus(str, Enum):
    """GCS upload status"""

    SUCCESS = "success"
    PARTIAL = "partial"
    FAILED = "failed"
    SKIPPED = "skipped"


class PipelineConfig(BaseModel):
    """파이프라인 실행 설정"""

    # 데이터 수집 설정
    youtube_count: int = Field(default=3, ge=1, le=10, description="YouTube 검색 결과 수")
    naver_count: int = Field(default=10, ge=5, le=30, description="네이버 쇼핑 검색 결과 수")
    include_comments: bool = Field(default=True, description="댓글 수집 여부")
    include_transcript: bool = Field(default=True, description="자막 수집 여부")

    # 콘텐츠 생성 설정
    generate_social: bool = Field(default=True, description="SNS 포스팅 생성 여부")
    generate_thumbnail: bool = Field(default=True, description="썸네일 생성 여부")
    generate_multi_thumbnails: bool = Field(default=False, description="다중 썸네일 생성 여부")
    thumbnail_count: int = Field(default=3, ge=1, le=5, description="생성할 썸네일 수")
    thumbnail_styles: list[str] | None = Field(
        default=None, description="썸네일 스타일 목록 (옵션)"
    )
    generate_video: bool = Field(default=True, description="비디오 생성 여부")
    video_duration: int = Field(default=8, ge=5, le=30, description="비디오 길이(초)")
    video_dual_phase_beta: bool = Field(
        default=False, description="Dual phase 비디오 생성 베타 플래그"
    )

    # AI 설정
    use_search_grounding: bool = Field(default=True, description="검색 그라운딩 사용 여부")
    max_comment_samples: int = Field(
        default=100,
        ge=10,
        le=300,
        description="X-Algorithm 분석에 사용할 최대 댓글 수",
    )

    # 저장 설정
    upload_to_gcs: bool = Field(default=True, description="GCS 업로드 여부")


class PipelineProgress(BaseModel):
    """파이프라인 실행 진행 상황"""

    STEP_ORDER: ClassVar[Tuple[PipelineStep, ...]] = (
        PipelineStep.DATA_COLLECTION,
        PipelineStep.YOUTUBE_COLLECTION,
        PipelineStep.NAVER_COLLECTION,
        PipelineStep.COMMENT_ANALYSIS,
        PipelineStep.STRATEGY_GENERATION,
        PipelineStep.SOCIAL_GENERATION,
        PipelineStep.THUMBNAIL_CREATION,
        PipelineStep.VIDEO_GENERATION,
        PipelineStep.UPLOAD,
        PipelineStep.COMPLETED,
    )

    STEP_WEIGHTS: ClassVar[dict[PipelineStep, int]] = {
        PipelineStep.DATA_COLLECTION: 5,
        PipelineStep.YOUTUBE_COLLECTION: 10,
        PipelineStep.NAVER_COLLECTION: 10,
        PipelineStep.COMMENT_ANALYSIS: 20,
        PipelineStep.STRATEGY_GENERATION: 10,
        PipelineStep.SOCIAL_GENERATION: 10,
        PipelineStep.THUMBNAIL_CREATION: 15,
        PipelineStep.VIDEO_GENERATION: 15,
        PipelineStep.UPLOAD: 5,
        PipelineStep.COMPLETED: 0,
    }

    _step_order: tuple[PipelineStep, ...] = PrivateAttr(default=STEP_ORDER)
    _total_weight: int = PrivateAttr(default=0)

    current_step: PipelineStep = Field(default=PipelineStep.INITIALIZED, description="현재 단계")
    step_number: int = Field(default=0, ge=0, description="현재 단계 번호")
    total_steps: int = Field(default=len(STEP_ORDER), ge=1, description="총 단계 수")
    message: str = Field(default="", description="진행 메시지")
    percentage: int = Field(default=0, ge=0, le=100, description="진행률")

    def update(self, step: PipelineStep, message: str = "") -> None:
        """진행 상황 업데이트"""
        self.current_step = step
        self.message = message

        if step == PipelineStep.INITIALIZED:
            self.step_number = 0
        elif step == PipelineStep.FAILED:
            # 실패 시 단계 번호 유지
            pass
        elif step in self._step_order:
            self.step_number = self._step_order.index(step) + 1

        # 단계별 진행률 계산 (설정 기반 동적)
        if step == PipelineStep.INITIALIZED:
            self.percentage = 0
        elif step == PipelineStep.FAILED:
            self.percentage = min(max(self.percentage, 0), 100)
        elif step == PipelineStep.COMPLETED:
            self.percentage = 100
        elif step in self._step_order:
            self.percentage = self._calculate_percentage(step)

    def configure_steps(self, config: "PipelineConfig") -> None:
        steps = [
            PipelineStep.DATA_COLLECTION,
            PipelineStep.YOUTUBE_COLLECTION,
            PipelineStep.NAVER_COLLECTION,
            PipelineStep.COMMENT_ANALYSIS,
            PipelineStep.STRATEGY_GENERATION,
        ]
        if config.generate_social:
            steps.append(PipelineStep.SOCIAL_GENERATION)
        if config.generate_thumbnail:
            steps.append(PipelineStep.THUMBNAIL_CREATION)
        if config.generate_video:
            steps.append(PipelineStep.VIDEO_GENERATION)
        if config.upload_to_gcs:
            steps.append(PipelineStep.UPLOAD)
        steps.append(PipelineStep.COMPLETED)

        self._step_order = tuple(steps)
        self.total_steps = len(self._step_order)
        self._total_weight = sum(
            self.STEP_WEIGHTS.get(step, 0)
            for step in self._step_order
            if step != PipelineStep.COMPLETED
        )

    def _calculate_percentage(self, step: PipelineStep) -> int:
        if self._total_weight <= 0:
            return 0

        accumulated = 0
        for s in self._step_order:
            if s == PipelineStep.COMPLETED:
                break
            accumulated += self.STEP_WEIGHTS.get(s, 0)
            if s == step:
                break

        return min(100, round((accumulated / self._total_weight) * 100))

    def model_post_init(self, __context) -> None:
        if self._total_weight <= 0:
            self._total_weight = sum(
                self.STEP_WEIGHTS.get(step, 0)
                for step in self._step_order
                if step != PipelineStep.COMPLETED
            )


class CollectedData(BaseModel):
    """수집된 데이터"""

    youtube_data: Optional[dict[str, Any]] = Field(default=None, description="YouTube 데이터")
    naver_data: Optional[dict[str, Any]] = Field(default=None, description="네이버 데이터")
    pain_points: list[dict[str, Any]] = Field(default_factory=list, description="페인 포인트")
    gain_points: list[dict[str, Any]] = Field(default_factory=list, description="게인 포인트")
    top_insights: list[dict[str, Any]] = Field(default_factory=list, description="핵심 인사이트 (X-Algorithm)")
    quality_report: Optional[dict[str, Any]] = Field(
        default=None, description="데이터 품질 보고서"
    )
    market_trends: Optional[dict[str, Any]] = Field(
        default=None, description="시장 트렌드 데이터"
    )


class GeneratedContent(BaseModel):
    """생성된 콘텐츠"""

    model_config = ConfigDict(arbitrary_types_allowed=True)

    thumbnail_data: Optional[bytes] = Field(default=None, description="썸네일 이미지 바이트")
    thumbnail_url: Optional[str] = Field(default=None, description="썸네일 URL")
    multi_thumbnails: list[dict[str, Any]] = Field(default_factory=list, description="다중 썸네일")
    video_bytes: Optional[bytes] = Field(default=None, description="비디오 바이트")
    video_path: Optional[str] = Field(default=None, description="비디오 경로")
    video_url: Optional[str] = Field(default=None, description="비디오 URL")


class PipelineResult(BaseModel):
    """파이프라인 실행 결과"""

    model_config = ConfigDict(arbitrary_types_allowed=True)

    success: bool = Field(..., description="success flag")
    product_name: str = Field(..., description="product name")
    config: Optional[PipelineConfig] = Field(default=None, description="pipeline config")
    collected_data: Optional[CollectedData] = Field(default=None, description="collected data")
    strategy: Optional[dict[str, Any]] = Field(default=None, description="strategy")
    generated_content: Optional[GeneratedContent] = Field(default=None, description="generated content")
    prompt_log: Optional[dict[str, Any]] = Field(default=None, description="prompt log")
    approval_status: str = Field(default="draft", description="approval status")
    audit_trail: list[dict[str, Any]] = Field(default_factory=list, description="audit trail")
    error_message: Optional[str] = Field(default=None, description="error message")
    upload_status: UploadStatus = Field(
        default=UploadStatus.SKIPPED,
        description="GCS upload status",
    )
    upload_errors: list[str] = Field(
        default_factory=list,
        description="Upload failure details",
    )
    executed_at: datetime = Field(default_factory=datetime.now, description="실행 시간")
    duration_seconds: float = Field(default=0.0, ge=0, description="실행 시간(초)")

