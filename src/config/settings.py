"""
환경변수 기반 설정 관리
Pydantic Settings를 사용하여 안전하게 API 키 및 설정 관리

Note: YouTube/Gemini는 Vertex AI를 사용하므로 GCP 서비스 계정으로 통합 인증
"""

from functools import lru_cache
import json
from typing import Optional

from pydantic import AliasChoices, Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict

AI_MODEL_RATIONALE = {
    "gemini-3-pro-preview": {
        "선택 이유": "텍스트 생성 + 멀티모달 분석 최적화",
        "대안 검토": ["GPT-4", "Claude"],
        "채택 근거": "GCP 네이티브 통합, 비용 효율성",
    },
    "veo-3.1-fast-generate-001": {
        "선택 이유": "빠른 영상 생성 속도",
        "채택 근거": "마케팅 캠페인의 시간 민감성 대응",
    },
}


class GCPSettings(BaseSettings):
    """GCP 설정 (Vertex AI 통합 인증)"""

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )

    project_id: str = Field(
        ...,
        validation_alias=AliasChoices("GOOGLE_CLOUD_PROJECT_ID", "GOOGLE_PROJECT_ID"),
    )
    location: str = Field(
        default="us-central1",
        validation_alias=AliasChoices("GOOGLE_CLOUD_LOCATION", "VERTEX_LOCATION"),
    )
    gcs_bucket_name: Optional[str] = Field(
        default=None, validation_alias="GCS_BUCKET_NAME"
    )
    credentials_path: Optional[str] = Field(
        default=None, validation_alias="GOOGLE_APPLICATION_CREDENTIALS"
    )
    data_store_id: Optional[str] = Field(
        default=None, validation_alias="DATA_STORE_ID"
    )

    # Vertex AI 통합 API 키 (YouTube, Gemini 공용)
    google_api_key: SecretStr = Field(..., validation_alias="GOOGLE_API_KEY")


class NaverSettings(BaseSettings):
    """네이버 API 설정"""

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )

    client_id: SecretStr = Field(..., validation_alias="NAVER_CLIENT_ID")
    client_secret: SecretStr = Field(..., validation_alias="NAVER_CLIENT_SECRET")


class AIModelSettings(BaseSettings):
    """AI 모델 설정"""

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )

    gemini_text_model: str = Field(
        default="gemini-3-pro-preview", validation_alias="GEMINI_TEXT_MODEL"
    )
    gemini_image_model: str = Field(
        default="gemini-3-pro-image-preview", validation_alias="GEMINI_IMAGE_MODEL"
    )
    veo_model_id: str = Field(
        default="veo-3.1-fast-generate-001", validation_alias="VEO_MODEL_ID"
    )


class NotionSettings(BaseSettings):
    """Notion API 설정"""

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )

    api_key: Optional[SecretStr] = Field(
        default=None, validation_alias="NOTION_API_KEY"
    )
    database_id: Optional[str] = Field(
        default=None, validation_alias="NOTION_DATABASE_ID"
    )


class AppSettings(BaseSettings):
    """애플리케이션 전체 설정"""

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )

    app_name: str = "제네시스코리아 스튜디오"
    debug: bool = Field(default=False, validation_alias="DEBUG")
    log_level: str = Field(default="INFO", validation_alias="LOG_LEVEL")
    output_dir: str = Field(default="outputs", validation_alias="OUTPUT_DIR")
    database_url: str = Field(
        default="sqlite+aiosqlite:///./data/auth.db",
        validation_alias="DATABASE_URL",
    )
    jwt_secret: str = Field(default="dev-secret", validation_alias="JWT_SECRET")
    jwt_expire_hours: int = Field(default=24, validation_alias="JWT_EXPIRE_HOURS")
    brand_banned_keywords_raw: str = Field(
        default="",
        validation_alias="BRAND_BANNED_KEYWORDS",
    )
    rag_data_stores_raw: str = Field(
        default="{}",
        validation_alias="RAG_DATA_STORES",
    )
    rag_ingestion_max_retries: int = Field(
        default=3,
        validation_alias="RAG_INGESTION_MAX_RETRIES",
    )
    rag_ingestion_backoff_seconds: float = Field(
        default=0.5,
        validation_alias="RAG_INGESTION_BACKOFF_SECONDS",
    )
    rag_ingestion_jitter_seconds: float = Field(
        default=0.1,
        validation_alias="RAG_INGESTION_JITTER_SECONDS",
    )


class Settings:
    """통합 설정 클래스"""

    def __init__(self) -> None:
        self.app = AppSettings()
        self.gcp = GCPSettings()  # type: ignore[call-arg]
        self.naver = NaverSettings()  # type: ignore[call-arg]
        self.notion = NotionSettings()
        self.models = AIModelSettings()

    @property
    def google_api_key(self) -> str:
        """Google API 키 반환 (YouTube, Gemini 공용)"""
        return self.gcp.google_api_key.get_secret_value()

    @property
    def notion_api_key(self) -> str:
        """Notion API 키 반환"""
        return self.notion.api_key.get_secret_value() if self.notion.api_key else ""

    @property
    def notion_database_id(self) -> str:
        """Notion Database ID 반환"""
        return self.notion.database_id or ""

    @property
    def brand_banned_keywords(self) -> list[str]:
        raw = self.app.brand_banned_keywords_raw
        if not raw:
            return []
        return [item.strip() for item in raw.split(",") if item.strip()]

    @property
    def rag_data_stores(self) -> dict[str, str]:
        raw = self.app.rag_data_stores_raw
        if not raw:
            return {}
        try:
            data = json.loads(raw)
        except json.JSONDecodeError:
            return {}
        if isinstance(data, dict):
            return {str(k): str(v) for k, v in data.items()}
        return {}

    def has_notion_api_key(self) -> bool:
        """Notion API 키 설정 여부"""
        return bool(self.notion.api_key and self.notion.api_key.get_secret_value())

    def get_missing_required_settings(self) -> list[str]:
        """필수 설정 누락 항목 반환"""
        missing = []
        if not self.gcp.project_id:
            missing.append("GOOGLE_CLOUD_PROJECT_ID")
        if not self.gcp.google_api_key.get_secret_value():
            missing.append("GOOGLE_API_KEY")
        if not self.naver.client_id.get_secret_value():
            missing.append("NAVER_CLIENT_ID")
        if not self.naver.client_secret.get_secret_value():
            missing.append("NAVER_CLIENT_SECRET")
        return missing

    def setup_environment(self) -> None:
        """GCP 환경변수 설정 (Vertex AI용)"""
        import os
        from pathlib import Path

        os.environ["GOOGLE_CLOUD_PROJECT"] = self.gcp.project_id
        os.environ["GOOGLE_CLOUD_LOCATION"] = self.gcp.location
        os.environ["GOOGLE_GENAI_USE_VERTEXAI"] = "True"

        if self.gcp.credentials_path:
            credentials_path = Path(self.gcp.credentials_path)
            if credentials_path.exists():
                os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = str(credentials_path)
            else:
                # 키 파일이 없으면 Workload Identity(ADC)로 전환
                if "GOOGLE_APPLICATION_CREDENTIALS" in os.environ:
                    del os.environ["GOOGLE_APPLICATION_CREDENTIALS"]


@lru_cache()
def get_settings() -> Settings:
    """캐시된 설정 인스턴스 반환"""
    return Settings()
