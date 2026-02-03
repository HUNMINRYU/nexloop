"""
스토리지 서비스 인터페이스 정의
"""
from abc import abstractmethod
from typing import Protocol, runtime_checkable


@runtime_checkable
class IStorageService(Protocol):
    """스토리지 서비스 프로토콜"""

    @abstractmethod
    def ensure_bucket(self) -> None:
        """버킷 존재 확인 및 필요 시 생성"""
        ...

    @abstractmethod
    def health_check(self) -> bool:
        """???? ?? ?? ??"""
        ...

    @property
    @abstractmethod
    def bucket_name(self) -> str | None:
        """?? ?? ??"""
        ...

    @abstractmethod
    def upload(
        self,
        data: bytes | dict,
        path: str,
        content_type: str = "application/json",
    ) -> bool:
        """데이터 업로드"""
        ...

    @abstractmethod
    def download(self, path: str) -> bytes | None:
        """데이터 다운로드"""
        ...

    @abstractmethod
    def list_files(self, prefix: str = "") -> list[str]:
        """파일 목록 조회"""
        ...

    @abstractmethod
    def get_public_url(self, path: str) -> str | None:
        """공개 URL 조회"""
        ...

    @abstractmethod
    def get_metadata(self, path: str) -> dict | None:
        """메타데이터 조회"""
        ...

    @abstractmethod
    def delete(self, path: str) -> bool:
        """파일 삭제"""
        ...

    @abstractmethod
    def exists(self, path: str) -> bool:
        """파일 존재 여부 확인"""
        ...
