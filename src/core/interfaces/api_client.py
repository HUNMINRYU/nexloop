"""
API 클라이언트 인터페이스 정의
"""
from abc import abstractmethod
from typing import Generic, Protocol, TypeVar, runtime_checkable

T = TypeVar("T")


@runtime_checkable
class IApiClient(Protocol):
    """모든 API 클라이언트의 기본 프로토콜"""

    @abstractmethod
    def is_configured(self) -> bool:
        """클라이언트가 올바르게 설정되었는지 확인"""
        ...

    @abstractmethod
    def health_check(self) -> bool:
        """API 연결 상태 확인"""
        ...


@runtime_checkable
class ISearchClient(IApiClient, Protocol, Generic[T]):
    """검색 기반 API 클라이언트 프로토콜"""

    @abstractmethod
    def search(self, query: str, max_results: int = 10) -> list[T]:
        """검색 실행"""
        ...


@runtime_checkable
class IYouTubeClient(ISearchClient, Protocol):
    """YouTube API 클라이언트 프로토콜"""

    @abstractmethod
    def get_video_details(self, video_id: str) -> dict | None:
        """비디오 상세 정보 조회"""
        ...

    @abstractmethod
    def get_video_comments(self, video_id: str, max_results: int = 100) -> list[dict]:
        """비디오 댓글 조회"""
        ...

    @abstractmethod
    def get_transcript(self, video_id: str) -> str | None:
        """비디오 자막 조회"""
        ...

    @abstractmethod
    def collect_video_data(
        self,
        product: dict,
        max_results: int = 5,
        include_comments: bool = True,
    ) -> dict:
        """제품 기반 YouTube 데이터 수집"""
        ...

    @abstractmethod
    def extract_pain_points(self, comments: list[dict]) -> list[dict]:
        """댓글에서 페인포인트 추출"""
        ...

    @abstractmethod
    def extract_gain_points(self, comments: list[dict]) -> list[dict]:
        """댓글에서 게인포인트 추출"""
        ...


@runtime_checkable
class INaverClient(ISearchClient, Protocol):
    """네이버 API 클라이언트 프로토콜"""

    @abstractmethod
    def search_shopping(self, query: str, display: int = 10) -> list[dict]:
        """네이버 쇼핑 검색"""
        ...

    @abstractmethod
    def analyze_competitors(self, products: list[dict]) -> dict:
        """경쟁사 분석"""
        ...

    @abstractmethod
    def search_blog(self, query: str, display: int = 10) -> list[dict]:
        """네이버 블로그 검색"""
        ...

    @abstractmethod
    def search_news(self, query: str, display: int = 10) -> list[dict]:
        """네이버 뉴스 검색"""
        ...
