from __future__ import annotations

import hashlib
import random
import time
from datetime import datetime, timezone
from typing import Any

from config.settings import get_settings
from core.interfaces.chatbot import IRAGClient
from core.models import PipelineResult
from utils.logger import get_logger

logger = get_logger(__name__)


class RagIngestionService:
    """Best-effort ingestion of internal signals into Discovery Engine."""

    def __init__(self, rag_client: IRAGClient) -> None:
        self._rag_client = rag_client
        self._settings = get_settings()
        self._recent_queries: dict[str, float] = {}

    def ingest_search_log(
        self,
        query: str,
        results: list[dict[str, Any]],
        user: Any | None = None,
    ) -> int:
        query = (query or "").strip()
        if not query:
            return 0
        if not self._should_ingest_query(query):
            return 0

        role = getattr(user, "role", None)
        email = getattr(user, "email", None)
        data_store_id = self._resolve_data_store_id('search', role)

        docs: list[dict[str, Any]] = []
        now_iso = self._now_iso()
        seen: set[str] = set()
        for idx, item in enumerate(results):
            title = self._coerce_text(item.get("title") or query, limit=256)
            snippet = self._coerce_text(item.get("snippet") or "", limit=1500)
            url = self._coerce_text(item.get("url") or "", limit=500)
            if not title and not snippet and not url:
                continue
            key = url or f"{title}|{snippet}"
            if key in seen:
                continue
            seen.add(key)
            if not snippet and not url:
                continue
            content = "\n".join(
                [
                    f"Query: {query}",
                    title,
                    snippet,
                    url,
                ]
            ).strip()
            doc_id = self._make_doc_id("search", f"{query}|{key}")
            docs.append(
                {
                    "id": doc_id,
                    "struct_data": {
                        "title": title,
                        "content": content,
                        "url": url,
                        "source_type": "search_log",
                        "query": query,
                        "user_role": role or "",
                        "user_email": email or "",
                        "created_at": now_iso,
                    },
                }
            )
            if len(docs) >= 5:
                break
        if not docs:
            doc_id = self._make_doc_id("search", query)
            docs.append(
                {
                    "id": doc_id,
                    "struct_data": {
                        "title": query,
                        "content": f"Query: {query}",
                        "url": "",
                        "source_type": "search_log",
                        "query": query,
                        "user_role": role or "",
                        "user_email": email or "",
                        "created_at": now_iso,
                    },
                }
            )

        return self._upsert_documents(docs, data_store_id=data_store_id)

    def ingest_manual_upload(
        self,
        items: list[Any],
        user: Any | None = None,
    ) -> int:
        if not items:
            return 0

        role = getattr(user, "role", None)
        email = getattr(user, "email", None)
        data_store_id = self._resolve_data_store_id(role, "internal")

        now_iso = self._now_iso()
        docs: list[dict[str, Any]] = []
        seen: set[str] = set()

        for item in items:
            if hasattr(item, "model_dump"):
                payload = item.model_dump()
            elif isinstance(item, dict):
                payload = item
            else:
                continue

            title = self._coerce_text(payload.get("title"), limit=256)
            content = self._coerce_text(payload.get("content"), limit=4000)
            if not title and not content:
                continue

            doc_type = self._coerce_text(
                payload.get("doc_type") or "internal_upload", limit=50
            )
            source = self._coerce_text(payload.get("source") or "", limit=200)
            campaign_name = self._coerce_text(
                payload.get("campaign_name") or "", limit=200
            )
            channel = self._coerce_text(payload.get("channel") or "", limit=100)
            region = self._coerce_text(payload.get("region") or "", limit=100)
            period_start = self._coerce_text(payload.get("period_start") or "", limit=50)
            period_end = self._coerce_text(payload.get("period_end") or "", limit=50)

            metrics = payload.get("metrics") or {}
            if hasattr(metrics, "model_dump"):
                metrics = metrics.model_dump()
            if not isinstance(metrics, dict):
                metrics = {}
            metrics_clean = {k: v for k, v in metrics.items() if v is not None}

            tags_raw = payload.get("tags") or []
            tags: list[str] = []
            if isinstance(tags_raw, list):
                for tag in tags_raw:
                    tag_text = self._coerce_text(tag, limit=50)
                    if tag_text:
                        tags.append(tag_text)

            key = f"{doc_type}|{title}|{content}|{source}|{period_start}|{period_end}"
            doc_id = self._make_doc_id("manual", key)
            if doc_id in seen:
                continue
            seen.add(doc_id)

            docs.append(
                {
                    "id": doc_id,
                    "struct_data": {
                        "title": title or "Untitled",
                        "content": content or title,
                        "doc_type": doc_type,
                        "source": source,
                        "campaign_name": campaign_name,
                        "channel": channel,
                        "region": region,
                        "period_start": period_start,
                        "period_end": period_end,
                        "metrics": metrics_clean,
                        "tags": tags,
                        "created_at": now_iso,
                        "user_role": role or "",
                        "user_email": email or "",
                    },
                }
            )

        return self._upsert_documents(docs, data_store_id=data_store_id)


    def _should_ingest_query(self, query: str, ttl_seconds: int = 60) -> bool:
        now = time.time()
        last = self._recent_queries.get(query)
        if last and (now - last) < ttl_seconds:
            return False
        self._recent_queries[query] = now
        return True

    def ingest_pipeline_result(self, result: PipelineResult) -> int:
        if not result or not result.success:
            return 0

        data_store_id = self._resolve_data_store_id('pipeline')
        now_iso = self._iso_or_now(result.executed_at)

        strategy = result.strategy or {}
        collected = result.collected_data
        market_trends = collected.market_trends if collected else None
        top_insights = []
        if collected and collected.top_insights:
            for item in collected.top_insights:
                content = item.get("content") if isinstance(item, dict) else str(item)
                if content:
                    top_insights.append(str(content))

        docs: list[dict[str, Any]] = []
        product_name = self._coerce_text(result.product_name, limit=200)

        summary = self._coerce_text(strategy.get("summary") or "", limit=2000)
        if summary:
            content = "\n\n".join(
                [
                    f"Product: {product_name}",
                    "Summary",
                    summary,
                ]
            )
            docs.append(
                {
                    "id": self._make_doc_id("pipeline-summary", f"{product_name}|{now_iso}"),
                    "struct_data": {
                        "title": f"Pipeline Summary - {product_name}",
                        "content": content,
                        "source_type": "pipeline_summary",
                        "product_name": product_name,
                        "created_at": now_iso,
                    },
                }
            )

        if top_insights:
            insights_text = "\n".join(f"- {self._coerce_text(item, 500)}" for item in top_insights[:20])
            content = "\n\n".join(
                [
                    f"Product: {product_name}",
                    "Top Insights",
                    insights_text,
                ]
            )
            docs.append(
                {
                    "id": self._make_doc_id("pipeline-insights", f"{product_name}|{now_iso}"),
                    "struct_data": {
                        "title": f"Pipeline Insights - {product_name}",
                        "content": content,
                        "source_type": "pipeline_insights",
                        "product_name": product_name,
                        "created_at": now_iso,
                    },
                }
            )

        hooks = strategy.get("hook_suggestions")
        if isinstance(hooks, list) and hooks:
            hooks_text = "\n".join(f"- {self._coerce_text(item, 300)}" for item in hooks[:20])
            content = "\n\n".join(
                [
                    f"Product: {product_name}",
                    "Hook Suggestions",
                    hooks_text,
                ]
            )
            docs.append(
                {
                    "id": self._make_doc_id("pipeline-hooks", f"{product_name}|{now_iso}"),
                    "struct_data": {
                        "title": f"Pipeline Hooks - {product_name}",
                        "content": content,
                        "source_type": "pipeline_hooks",
                        "product_name": product_name,
                        "created_at": now_iso,
                    },
                }
            )

        usp = strategy.get("unique_selling_point")
        if isinstance(usp, list) and usp:
            usp_text = "\n".join(f"- {self._coerce_text(item, 300)}" for item in usp[:20])
            content = "\n\n".join(
                [
                    f"Product: {product_name}",
                    "Unique Selling Points",
                    usp_text,
                ]
            )
            docs.append(
                {
                    "id": self._make_doc_id("pipeline-usp", f"{product_name}|{now_iso}"),
                    "struct_data": {
                        "title": f"Pipeline USP - {product_name}",
                        "content": content,
                        "source_type": "pipeline_usp",
                        "product_name": product_name,
                        "created_at": now_iso,
                    },
                }
            )

        if isinstance(market_trends, dict):
            issues = market_trends.get("issues")
            if isinstance(issues, list) and issues:
                issues_text = []
                for item in issues[:10]:
                    if isinstance(item, dict):
                        title = self._coerce_text(item.get("title"), 200)
                        summary = self._coerce_text(item.get("summary"), 500)
                        issues_text.append(f"- {title}: {summary}".strip())
                    else:
                        issues_text.append(f"- {self._coerce_text(item, 500)}")
                content = "\n\n".join(
                    [
                        f"Product: {product_name}",
                        "Market Trends",
                        "\n".join(issues_text),
                    ]
                )
                docs.append(
                    {
                        "id": self._make_doc_id("pipeline-trends", f"{product_name}|{now_iso}"),
                        "struct_data": {
                            "title": f"Pipeline Trends - {product_name}",
                            "content": content,
                            "source_type": "pipeline_trends",
                            "product_name": product_name,
                            "created_at": now_iso,
                        },
                    }
                )

        if not docs:
            return 0

        return self._upsert_documents(docs, data_store_id=data_store_id)

    def _resolve_data_store_id(self, *roles: str | None) -> str | None:
        mapping = self._settings.rag_data_stores
        for role in roles:
            if role and role in mapping:
                return mapping[role]
        return self._settings.gcp.data_store_id

    def _upsert_documents(
        self,
        documents: list[dict[str, Any]],
        data_store_id: str | None,
    ) -> int:
        if not documents:
            return 0
        if not data_store_id:
            logger.warning("RAG ingestion skipped: data_store_id missing.")
            return 0
        if hasattr(self._rag_client, "is_configured"):
            try:
                if not self._rag_client.is_configured():
                    logger.warning("RAG ingestion skipped: client not configured.")
                    return 0
            except Exception:
                pass
        if not hasattr(self._rag_client, "upsert_documents"):
            logger.warning("RAG ingestion skipped: upsert_documents not supported.")
            return 0
        max_retries = max(1, int(self._settings.app.rag_ingestion_max_retries or 1))
        backoff = max(0.0, float(self._settings.app.rag_ingestion_backoff_seconds or 0.0))
        jitter = max(0.0, float(self._settings.app.rag_ingestion_jitter_seconds or 0.0))

        last_error: Exception | None = None
        for attempt in range(1, max_retries + 1):
            try:
                ingested = int(
                    self._rag_client.upsert_documents(
                        documents,
                        data_store_id=data_store_id,
                    )
                )
                if ingested > 0:
                    if attempt > 1:
                        logger.info(
                            "RAG ingestion succeeded after retry.",
                        )
                    return ingested
                logger.warning(
                    "RAG ingestion returned 0 items (attempt %s/%s).",
                    attempt,
                    max_retries,
                )
            except Exception as exc:
                last_error = exc
                logger.warning(
                    "RAG ingestion failed (attempt %s/%s): %s",
                    attempt,
                    max_retries,
                    exc,
                )

            if attempt < max_retries:
                sleep_for = backoff * (2 ** (attempt - 1))
                if jitter:
                    sleep_for += random.uniform(0, jitter)
                if sleep_for > 0:
                    time.sleep(sleep_for)

        if last_error:
            logger.error("RAG ingestion failed after retries: %s", last_error)
        else:
            logger.warning("RAG ingestion exhausted retries with zero ingested items.")
        return 0

    @staticmethod
    def _now_iso() -> str:
        return datetime.now(timezone.utc).isoformat()

    @staticmethod
    def _iso_or_now(value: Any) -> str:
        if isinstance(value, datetime):
            return value.isoformat()
        return datetime.now(timezone.utc).isoformat()

    @staticmethod
    def _coerce_text(value: Any, limit: int = 2000) -> str:
        text = str(value or "").strip()
        if len(text) > limit:
            return text[:limit]
        return text

    @staticmethod
    def _make_doc_id(prefix: str, key: str) -> str:
        digest = hashlib.sha256(key.encode("utf-8")).hexdigest()[:32]
        return f"{prefix}-{digest}"
