"""
네이버 쇼핑 API 클라이언트
"""
import requests

from core.exceptions import NaverAPIError
from utils.logger import get_logger

logger = get_logger(__name__)


class NaverClient:
    """네이버 API 클라이언트"""

    SHOPPING_API_URL = "https://openapi.naver.com/v1/search/shop.json"
    BLOG_API_URL = "https://openapi.naver.com/v1/search/blog.json"
    NEWS_API_URL = "https://openapi.naver.com/v1/search/news.json"

    def __init__(self, client_id: str, client_secret: str) -> None:
        self._client_id = client_id
        self._client_secret = client_secret

    def is_configured(self) -> bool:
        """API 키가 설정되었는지 확인"""
        return bool(self._client_id and self._client_secret)

    def health_check(self) -> bool:
        """API 연결 상태 확인"""
        try:
            self.search_shopping("테스트", display=1)
            return True
        except Exception:
            return False

    def search(self, query: str, max_results: int = 10) -> list[dict]:
        """검색 실행 (ISearchClient 구현)"""
        return self.search_shopping(query, display=max_results)

    def search_shopping(self, query: str, display: int = 10) -> list[dict]:
        """네이버 쇼핑 상품 검색"""
        data = self._search(self.SHOPPING_API_URL, query, display)
        products = []

        for item in data.get("items", []):
            products.append({
                "product_id": item.get("productId", ""),
                "title": item.get("title", "").replace("<b>", "").replace("</b>", ""),
                "price": int(item.get("lprice", 0)),
                "image": item.get("image", ""),
                "brand": item.get("brand", ""),
                "mall": item.get("mallName", ""),
                "link": item.get("link", ""),
                "category1": item.get("category1", ""),
                "category2": item.get("category2", ""),
                "category3": item.get("category3", ""),
                "category4": item.get("category4", ""),
            })

        logger.info(f"네이버 쇼핑 검색 완료: '{query}' -> {len(products)}개 결과")
        return products

    def search_blog(self, query: str, display: int = 10) -> list[dict]:
        """네이버 블로그 검색"""
        data = self._search(self.BLOG_API_URL, query, display)
        results = []
        for item in data.get("items", []):
            results.append({
                "title": item.get("title", "").replace("<b>", "").replace("</b>", ""),
                "description": item.get("description", "").replace("<b>", "").replace("</b>", ""),
                "link": item.get("link", ""),
                "blogger": item.get("bloggername", ""),
                "post_date": item.get("postdate", ""),
            })
        logger.info(f"네이버 블로그 검색 완료: '{query}' -> {len(results)}개 결과")
        return results

    def search_news(self, query: str, display: int = 10) -> list[dict]:
        """네이버 뉴스 검색"""
        data = self._search(self.NEWS_API_URL, query, display)
        results = []
        for item in data.get("items", []):
            results.append({
                "title": item.get("title", "").replace("<b>", "").replace("</b>", ""),
                "description": item.get("description", "").replace("<b>", "").replace("</b>", ""),
                "link": item.get("link", ""),
                "origin": item.get("originallink", ""),
                "published_at": item.get("pubDate", ""),
            })
        logger.info(f"네이버 뉴스 검색 완료: '{query}' -> {len(results)}개 결과")
        return results

    def _search(self, url: str, query: str, display: int) -> dict:
        if not self.is_configured():
            logger.warning("네이버 API 자격증명이 설정되지 않았습니다.")
            return {"items": []}

        headers = {
            "X-Naver-Client-Id": self._client_id,
            "X-Naver-Client-Secret": self._client_secret,
        }
        params: dict[str, str | int] = {"query": query, "display": display}

        try:
            response = requests.get(
                url,
                headers=headers,
                params=params,
                timeout=10,
            )

            if response.status_code != 200:
                raise NaverAPIError(
                    f"네이버 API 오류: {response.status_code}",
                    {"status_code": response.status_code, "query": query},
                )

            return response.json()

        except NaverAPIError:
            raise
        except Exception as e:
            logger.error(f"네이버 검색 실패: {e}")
            raise NaverAPIError(f"네이버 검색 실패: {e}", {"query": query})

    def analyze_competitors(self, products: list[dict]) -> dict:
        """경쟁사 분석 - 가격 통계"""
        if not products:
            return {
                "total_products": 0,
                "min_price": 0,
                "max_price": 0,
                "avg_price": 0,
                "top_brands": [],
                "top_malls": [],
                "price_distribution": {},
            }

        prices = [p["price"] for p in products if p.get("price", 0) > 0]
        if not prices:
            return {
                "total_products": len(products),
                "min_price": 0,
                "max_price": 0,
                "avg_price": 0,
                "top_brands": [],
                "top_malls": [],
                "price_distribution": {},
            }

        # 브랜드/판매처 집계
        brand_counts: dict[str, int] = {}
        mall_counts: dict[str, int] = {}

        for p in products:
            brand = p.get("brand", "")
            mall = p.get("mall", "")
            if brand:
                brand_counts[brand] = brand_counts.get(brand, 0) + 1
            if mall:
                mall_counts[mall] = mall_counts.get(mall, 0) + 1

        top_brands = sorted(brand_counts.items(), key=lambda x: x[1], reverse=True)[:5]
        top_malls = sorted(mall_counts.items(), key=lambda x: x[1], reverse=True)[:5]

        # 가격대별 분포
        price_ranges = {
            "0-10000": 0,
            "10000-30000": 0,
            "30000-50000": 0,
            "50000-100000": 0,
            "100000+": 0,
        }
        for price in prices:
            if price < 10000:
                price_ranges["0-10000"] += 1
            elif price < 30000:
                price_ranges["10000-30000"] += 1
            elif price < 50000:
                price_ranges["30000-50000"] += 1
            elif price < 100000:
                price_ranges["50000-100000"] += 1
            else:
                price_ranges["100000+"] += 1

        return {
            "total_products": len(products),
            "min_price": min(prices),
            "max_price": max(prices),
            "avg_price": sum(prices) // len(prices),
            "top_brands": [b[0] for b in top_brands],
            "top_malls": [m[0] for m in top_malls],
            "price_distribution": price_ranges,
        }
