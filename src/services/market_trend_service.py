"""
시장 트렌드 분석 서비스
Discovery Engine 검색 결과를 요약
"""

from typing import Any

from core.interfaces.chatbot import IRAGClient
from utils.logger import log_info, log_warning


class MarketTrendService:
    """시장 트렌드 분석 서비스"""

    def __init__(self, rag_client: IRAGClient) -> None:
        self._rag_client = rag_client

    def get_market_trends(self, product: dict, max_results: int = 5) -> dict[str, Any]:
        product_name = product.get("name", "")
        product_category = product.get("category", "")
        query = " ".join([item for item in [product_category, product_name, "시장 동향"] if item])

        if not query.strip():
            log_warning("시장 동향 검색을 위한 쿼리가 비어 있습니다.")
            return {"query": "", "issues": [], "raw_results": []}

        results = self._rag_client.search(query, max_results=max_results)

        issues = []
        for item in results[:3]:
            issues.append({
                "title": item.get("title", ""),
                "summary": item.get("snippet", ""),
                "url": item.get("url", ""),
            })

        log_info(f"시장 동향 검색 완료: '{query}' -> {len(issues)}개 이슈")
        return {"query": query, "issues": issues, "raw_results": results}
