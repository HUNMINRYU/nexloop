"""
Google Cloud Storage 서비스
"""

import json
import re
import uuid
from datetime import datetime
from typing import Any

from google.api_core.exceptions import Forbidden, NotFound
from google.cloud import storage

from core.exceptions import GCSDownloadError, GCSUploadError
from utils.logger import get_logger

logger = get_logger(__name__)


class GCSStorage:
    """Google Cloud Storage 서비스"""

    def __init__(
        self,
        bucket_name: str | None,
        project_id: str | None = None,
        location: str | None = None,
    ) -> None:
        self._bucket_name = bucket_name
        self._project_id = project_id
        self._location = location
        self._client = None

    def _get_client(self) -> storage.Client:
        """Storage 클라이언트 인스턴스 반환 (지연 초기화)"""
        if self._client is None:
            self._client = storage.Client(project=self._project_id)
        return self._client

    def _get_bucket(self) -> storage.Bucket:
        """버킷 인스턴스 반환"""
        return self._get_client().bucket(self._bucket_name)

    def _generate_bucket_name(self) -> str:
        base = self._project_id or "nexloop-korea"
        slug = re.sub(r"[^a-z0-9-]", "-", base.lower())
        suffix = datetime.utcnow().strftime("%Y%m%d") + "-" + uuid.uuid4().hex[:6]
        name = f"{slug}-nexloop-korea-{suffix}"
        return name[:63].strip("-")

    def ensure_bucket(self) -> None:
        """버킷 존재 확인 및 필요 시 생성"""
        client = self._get_client()

        if not self._bucket_name:
            self._bucket_name = self._generate_bucket_name()

        bucket = client.bucket(self._bucket_name)
        try:
            if not bucket.exists():
                client.create_bucket(bucket, location=self._location)
                logger.info(f"GCS 버킷 생성: {self._bucket_name}")
        except Forbidden:
            # Some service accounts lack buckets.get but can still upload objects.
            logger.warning(
                "GCS 버킷 존재 여부를 확인할 권한이 없습니다. "
                "버킷이 이미 존재한다고 가정하고 업로드를 시도합니다."
            )
        except NotFound:
            # Bucket truly missing and cannot be checked/created.
            raise

    def is_configured(self) -> bool:
        """설정 확인"""
        return bool(self._bucket_name)

    def health_check(self) -> bool:
        """연결 상태 확인"""
        try:
            self.ensure_bucket()
            return True
        except Exception:
            return False

    @property
    def bucket_name(self) -> str | None:
        return self._bucket_name

    def upload(
        self,
        data: bytes | dict | str,
        path: str,
        content_type: str = "application/json",
    ) -> bool:
        """데이터 업로드"""
        try:
            self.ensure_bucket()
            if not path or not isinstance(path, str):
                raise ValueError("업로드 경로가 유효하지 않습니다.")
            bucket = self._get_bucket()
            blob = bucket.blob(path)

            if content_type == "application/json" and isinstance(data, dict):
                blob.upload_from_string(
                    json.dumps(data, ensure_ascii=False, indent=2),
                    content_type=content_type,
                )
            elif isinstance(data, str):
                blob.upload_from_string(data, content_type=content_type)
            elif isinstance(data, bytes):
                blob.upload_from_string(data, content_type=content_type)
            else:
                raise ValueError(f"지원하지 않는 데이터 타입: {type(data)}")

            logger.info(f"GCS 업로드 완료: gs://{self._bucket_name}/{path}")
            return True

        except Exception as e:
            logger.error(f"GCS 업로드 실패: {e}")
            raise GCSUploadError(f"GCS 업로드 실패: {e}", path=path)

    def download(self, path: str) -> bytes | None:
        """바이너리 데이터 다운로드"""
        try:
            bucket = self._get_bucket()
            blob = bucket.blob(path)
            return blob.download_as_bytes()
        except Exception as e:
            logger.error(f"GCS 다운로드 실패: {e}")
            raise GCSDownloadError(f"GCS 다운로드 실패: {e}", path=path)

    def download_text(self, path: str) -> str | None:
        """텍스트 데이터 다운로드"""
        try:
            bucket = self._get_bucket()
            blob = bucket.blob(path)
            return blob.download_as_text()
        except Exception as e:
            logger.error(f"GCS 텍스트 다운로드 실패: {e}")
            return None

    def download_json(self, path: str) -> dict[str, Any] | None:
        """JSON 데이터 다운로드"""
        try:
            text = self.download_text(path)
            if text:
                return json.loads(text)
            return None
        except Exception as e:
            logger.error(f"GCS JSON 다운로드 실패: {e}")
            return None

    def list_files(self, prefix: str = "") -> list[str]:
        """파일 목록 조회"""
        try:
            bucket = self._get_bucket()
            blobs = bucket.list_blobs(prefix=prefix)
            return [blob.name for blob in blobs]
        except Exception as e:
            logger.error(f"GCS 목록 조회 실패: {e}")
            return []

    def get_public_url(self, path: str) -> str | None:
        """공개 URL 반환"""
        try:
            bucket = self._get_bucket()
            blob = bucket.blob(path)

            if blob.exists():
                return f"https://storage.googleapis.com/{self._bucket_name}/{path}"
            return None
        except Exception as e:
            logger.error(f"공개 URL 조회 실패: {e}")
            return None

    def get_metadata(self, path: str) -> dict[str, Any] | None:
        """메타데이터 조회"""
        try:
            bucket = self._get_bucket()
            blob = bucket.blob(path)
            if not blob.exists():
                return None
            blob.reload()
            return {
                "name": blob.name,
                "size": blob.size,
                "updated": blob.updated.isoformat() if blob.updated else None,
                "content_type": blob.content_type,
                "md5_hash": blob.md5_hash,
                "crc32c": blob.crc32c,
                "generation": blob.generation,
                "metageneration": blob.metageneration,
            }
        except Exception as e:
            logger.error(f"GCS 메타데이터 조회 실패: {e}")
            return None

    def get_signed_url(self, path: str, expiration_minutes: int = 60) -> str | None:
        """서명된 URL 반환 (만료 시간 설정)"""
        try:
            from datetime import timedelta

            bucket = self._get_bucket()
            blob = bucket.blob(path)

            if blob.exists():
                return blob.generate_signed_url(
                    expiration=timedelta(minutes=expiration_minutes),
                    method="GET",
                )
            return None
        except Exception as e:
            logger.error(f"서명된 URL 생성 실패: {e}")
            return None

    def delete(self, path: str) -> bool:
        """파일 삭제"""
        try:
            bucket = self._get_bucket()
            blob = bucket.blob(path)
            blob.delete()
            logger.info(f"GCS 파일 삭제: {path}")
            return True
        except Exception as e:
            logger.error(f"GCS 삭제 실패: {e}")
            return False

    def exists(self, path: str) -> bool:
        """파일 존재 여부 확인"""
        try:
            bucket = self._get_bucket()
            blob = bucket.blob(path)
            return blob.exists()
        except Exception:
            return False

    def copy(self, source_path: str, dest_path: str) -> bool:
        """파일 복사"""
        try:
            bucket = self._get_bucket()
            source_blob = bucket.blob(source_path)
            bucket.copy_blob(source_blob, bucket, dest_path)
            logger.info(f"GCS 파일 복사: {source_path} -> {dest_path}")
            return True
        except Exception as e:
            logger.error(f"GCS 복사 실패: {e}")
            return False
