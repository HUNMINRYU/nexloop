"""
YouTube API 클라이언트
YouTube Data API v3를 사용한 비디오 검색 및 댓글 수집
"""


from googleapiclient.discovery import build
from youtube_transcript_api import YouTubeTranscriptApi

from config.constants import YOUTUBE_LANGUAGES
from core.exceptions import YouTubeAPIError
from utils.cache import cached
from utils.logger import get_logger

logger = get_logger(__name__)


class YouTubeClient:
    """YouTube API 클라이언트"""

    def __init__(self, api_key: str) -> None:
        self._api_key = api_key
        self._youtube = None

    def _get_client(self):
        """YouTube API 클라이언트 인스턴스 반환 (지연 초기화)"""
        if self._youtube is None:
            self._youtube = build("youtube", "v3", developerKey=self._api_key)
        return self._youtube

    def is_configured(self) -> bool:
        """API 키가 설정되었는지 확인"""
        return bool(self._api_key)

    def health_check(self) -> bool:
        """API 연결 상태 확인"""
        try:
            self._get_client().search().list(
                part="id", q="test", maxResults=1
            ).execute()
            return True
        except Exception:
            return False

    @cached(ttl=300, cache_key_prefix="youtube")
    def search(self, query: str, max_results: int = 3) -> list[dict]:
        """YouTube 비디오 검색"""
        try:
            youtube = self._get_client()
            request = youtube.search().list(
                part="snippet",
                q=query,
                type="video",
                maxResults=max_results,
                order="relevance",
                regionCode="KR",
                relevanceLanguage="ko",
            )
            response = request.execute()

            videos = []
            for item in response.get("items", []):
                videos.append(
                    {
                        "id": item["id"]["videoId"],
                        "title": item["snippet"]["title"],
                        "description": item["snippet"]["description"],
                        "thumbnail": item["snippet"]["thumbnails"]["medium"]["url"],
                        "channel": item["snippet"]["channelTitle"],
                        "published_at": item["snippet"]["publishedAt"],
                    }
                )

            logger.info(f"YouTube 검색 완료: '{query}' -> {len(videos)}개 결과")
            return videos

        except Exception as e:
            logger.error(f"YouTube 검색 실패: {e}")
            raise YouTubeAPIError(f"YouTube 검색 실패: {e}", {"query": query})

    @cached(ttl=600, cache_key_prefix="youtube")
    def get_video_details(self, video_id: str) -> dict | None:
        """비디오 상세 정보 조회"""
        try:
            youtube = self._get_client()
            request = youtube.videos().list(part="snippet,statistics", id=video_id)
            response = request.execute()

            if not response.get("items"):
                return None

            item = response["items"][0]
            return {
                "id": video_id,
                "title": item["snippet"]["title"],
                "description": item["snippet"]["description"],
                "channel": item["snippet"]["channelTitle"],
                "published_at": item["snippet"]["publishedAt"],
                "view_count": int(item["statistics"].get("viewCount", 0)),
                "like_count": int(item["statistics"].get("likeCount", 0)),
                "comment_count": int(item["statistics"].get("commentCount", 0)),
            }
        except Exception as e:
            logger.error(f"비디오 상세 정보 조회 실패: {e}")
            return None

    @cached(ttl=120, cache_key_prefix="youtube")
    def get_video_comments(self, video_id: str, max_results: int = 20) -> list[dict]:
        """비디오 댓글 수집"""
        try:
            youtube = self._get_client()
            request = youtube.commentThreads().list(
                part="snippet",
                videoId=video_id,
                maxResults=max_results,
                order="relevance",
                textFormat="plainText",
            )
            response = request.execute()

            comments = []
            for item in response.get("items", []):
                comment = item["snippet"]["topLevelComment"]["snippet"]
                comments.append(
                    {
                        "text": comment["textDisplay"],
                        "likes": comment.get("likeCount", 0),
                        "author": comment.get("authorDisplayName", ""),
                        "published_at": comment.get("publishedAt", ""),
                    }
                )

            # 좋아요 순 정렬
            return sorted(comments, key=lambda x: x["likes"], reverse=True)

        except Exception:
            # 댓글 비활성화 등의 경우 빈 리스트 반환
            return []

    def get_transcript(self, video_id: str) -> str | None:
        """비디오 자막 추출"""
        try:
            transcript = YouTubeTranscriptApi.get_transcript(  # type: ignore[attr-defined]
                video_id, languages=YOUTUBE_LANGUAGES
            )
            return " ".join([t["text"] for t in transcript])
        except Exception:
            return None

    def collect_video_data(
        self,
        product: dict,
        max_results: int = 5,
        include_comments: bool = True,
    ) -> dict:
        """제품 기반 YouTube 데이터 수집"""
        # 검색 키워드 생성
        keywords = [
            product["name"],
            f"{product['target']} 퇴치",
            f"{product['category']} 추천",
        ]

        collected_videos = []
        all_comments = []
        seen_video_ids: set[str] = set()
        video_limit = max(1, int(max_results))

        for keyword in keywords[:2]:  # 상위 2개 키워드
            try:
                videos = self.search(keyword, video_limit)
                if len(videos) > video_limit:
                    videos = videos[:video_limit]
                for v in videos:
                    if v["id"] in seen_video_ids:
                        continue
                    seen_video_ids.add(v["id"])
                    transcript = self.get_transcript(v["id"])

                    comments = []
                    if include_comments:
                        comments = self.get_video_comments(v["id"], max_results=30)
                        all_comments.extend(comments)

                    collected_videos.append(
                        {
                            "keyword": keyword,
                            "video_id": v["id"],
                            "title": v["title"],
                            "description": v["description"],
                            "transcript": transcript[:2000]
                            if transcript
                            else v["description"][:500],
                            "thumbnail": v.get("thumbnail", ""),
                            "channel": v.get("channel", ""),
                            "comments_count": len(comments),
                        }
                    )
            except YouTubeAPIError:
                continue

        # 페인/게인 포인트 분석
        pain_points = (
            self.extract_pain_points(all_comments) if include_comments else []
        )
        gain_points = (
            self.extract_gain_points(all_comments) if include_comments else []
        )

        return {
            "product": product,
            "videos": collected_videos,
            "comments_total": len(all_comments),
            "pain_points": pain_points,
            "gain_points": gain_points,
            "top_comments": all_comments[:20] if all_comments else [],
        }

    def extract_pain_points(self, comments: list[dict]) -> list[dict]:
        """댓글에서 페인포인트 추출"""
        pain_keywords = [
            "안됨",
            "안돼",
            "효과없",
            "효과 없",
            "별로",
            "실망",
            "냄새",
            "불편",
            "어려",
            "비싸",
            "오래",
            "느리",
            "힘들",
            "짜증",
            "못",
            "안 ",
            "없어",
            "부족",
            "문제",
            "고장",
            "AS",
            "환불",
            "반품",
        ]

        pain_comments = []
        for comment in comments:
            text = comment["text"]
            for keyword in pain_keywords:
                if keyword in text:
                    pain_comments.append(
                        {
                            "text": text[:200],
                            "keyword": keyword,
                            "likes": comment["likes"],
                        }
                    )
                    break

        return pain_comments[:10]

    def extract_gain_points(self, comments: list[dict]) -> list[dict]:
        """댓글에서 게인포인트 추출"""
        gain_keywords = [
            "좋아",
            "최고",
            "효과",
            "추천",
            "만족",
            "대박",
            "잘",
            "빠르",
            "확실",
            "깨끗",
            "사라",
            "없어졌",
            "해결",
            "굿",
            "완전",
            "감사",
            "찐",
        ]

        gain_comments = []
        for comment in comments:
            text = comment["text"]
            for keyword in gain_keywords:
                if keyword in text:
                    gain_comments.append(
                        {
                            "text": text[:200],
                            "keyword": keyword,
                            "likes": comment["likes"],
                        }
                    )
                    break

        return gain_comments[:10]
