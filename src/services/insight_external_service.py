from __future__ import annotations

from typing import Any

from services.naver_service import NaverService
from services.rag_ingestion_service import RagIngestionService
from utils.logger import get_logger

logger = get_logger(__name__)


class InsightExternalService:
    """Collect external insight sources and ingest them into Discovery Engine."""

    def __init__(
        self,
        naver_service: NaverService,
        rag_ingestion_service: RagIngestionService,
    ) -> None:
        self._naver = naver_service
        self._rag_ingestion = rag_ingestion_service

    def ingest_naver(
        self,
        query: str,
        max_results: int = 10,
        include_products: bool = True,
        include_blogs: bool = True,
        include_news: bool = True,
        meta: dict[str, str | None] | None = None,
        user: Any | None = None,
    ) -> dict[str, int]:
        safe_query = (query or "").strip()
        if not safe_query:
            return {"ingested": 0, "items": 0, "products": 0, "blogs": 0, "news": 0}

        meta = meta or {}
        items: list[dict[str, Any]] = []
        products: list[dict[str, Any]] = []
        blogs: list[dict[str, Any]] = []
        news: list[dict[str, Any]] = []

        if include_products:
            try:
                products = self._naver.search_products(safe_query, max_results)
            except Exception as exc:
                logger.warning(f"Naver shopping search failed: {exc}")

        if include_blogs:
            try:
                blogs = self._naver.search_blog(safe_query, max_results)
            except Exception as exc:
                logger.warning(f"Naver blog search failed: {exc}")

        if include_news:
            try:
                news = self._naver.search_news(safe_query, max_results)
            except Exception as exc:
                logger.warning(f"Naver news search failed: {exc}")

        for item in products:
            title = item.get("title") or safe_query
            content = "\n".join(
                [
                    f"Product: {title}",
                    f"Price: {item.get('price', '')}",
                    f"Brand: {item.get('brand', '')}",
                    f"Mall: {item.get('mall', '')}",
                    f"Categories: {item.get('category1', '')} {item.get('category2', '')}",
                    f"Link: {item.get('link', '')}",
                ]
            ).strip()
            items.append(
                {
                    "title": title,
                    "content": content,
                    "doc_type": "trend_search",
                    "source": "naver_shopping",
                    "campaign_name": meta.get("campaign_name"),
                    "channel": meta.get("channel"),
                    "region": meta.get("region"),
                    "period_start": meta.get("period_start"),
                    "period_end": meta.get("period_end"),
                    "tags": [safe_query, "naver", "shopping"],
                }
            )

        for item in blogs:
            title = item.get("title") or safe_query
            content = "\n".join(
                [
                    f"Title: {title}",
                    item.get("description", ""),
                    f"Blogger: {item.get('blogger', '')}",
                    f"Date: {item.get('post_date', '')}",
                    f"Link: {item.get('link', '')}",
                ]
            ).strip()
            items.append(
                {
                    "title": title,
                    "content": content,
                    "doc_type": "social_trend",
                    "source": "naver_blog",
                    "campaign_name": meta.get("campaign_name"),
                    "channel": meta.get("channel"),
                    "region": meta.get("region"),
                    "period_start": meta.get("period_start"),
                    "period_end": meta.get("period_end"),
                    "tags": [safe_query, "naver", "blog"],
                }
            )

        for item in news:
            title = item.get("title") or safe_query
            content = "\n".join(
                [
                    f"Title: {title}",
                    item.get("description", ""),
                    f"Published: {item.get('published_at', '')}",
                    f"Link: {item.get('link', '')}",
                    f"Origin: {item.get('origin', '')}",
                ]
            ).strip()
            items.append(
                {
                    "title": title,
                    "content": content,
                    "doc_type": "news_summary",
                    "source": "naver_news",
                    "campaign_name": meta.get("campaign_name"),
                    "channel": meta.get("channel"),
                    "region": meta.get("region"),
                    "period_start": meta.get("period_start"),
                    "period_end": meta.get("period_end"),
                    "tags": [safe_query, "naver", "news"],
                }
            )

        ingested = self._rag_ingestion.ingest_manual_upload(items, user)
        return {
            "ingested": int(ingested),
            "items": len(items),
            "products": len(products),
            "blogs": len(blogs),
            "news": len(news),
        }
