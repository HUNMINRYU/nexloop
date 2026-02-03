from __future__ import annotations

from collections import Counter
from datetime import datetime
from typing import Any

from core.interfaces.chatbot import IRAGClient
from services.rag_ingestion_service import RagIngestionService


class InsightReportService:
    """Generate daily insight reports and store them in Discovery Engine."""

    def __init__(self, rag_client: IRAGClient, rag_ingestion: RagIngestionService) -> None:
        self._rag_client = rag_client
        self._rag_ingestion = rag_ingestion

    def generate_daily_report(
        self,
        query: str,
        max_results: int,
        data_store_id: str | None,
        doc_type: str | None = None,
        campaign_name: str | None = None,
        channel: str | None = None,
        region: str | None = None,
        period_start: str | None = None,
        period_end: str | None = None,
        title: str | None = None,
        user: Any | None = None,
    ) -> dict[str, Any]:
        safe_query = (query or "").strip()
        if not safe_query:
            return {"ingested": 0, "report": None}

        results = self._rag_client.search(
            safe_query,
            max_results=max_results,
            data_store_id=data_store_id,
        )

        filtered = [
            item
            for item in results
            if self._matches_filters(
                item,
                doc_type,
                campaign_name,
                channel,
                region,
                period_start,
                period_end,
            )
        ]

        report = self._build_report(
            query=safe_query,
            items=filtered,
            title=title,
            campaign_name=campaign_name,
            channel=channel,
            region=region,
            period_start=period_start,
            period_end=period_end,
        )

        ingested = 0
        if report:
            ingested = self._rag_ingestion.ingest_manual_upload([report], user)

        return {
            "ingested": int(ingested),
            "report": report,
            "items": len(filtered),
        }

    @staticmethod
    def _parse_dt(value: str | None) -> datetime | None:
        if not value:
            return None
        try:
            return datetime.fromisoformat(value.replace("Z", "+00:00"))
        except ValueError:
            return None

    @staticmethod
    def _normalize(value: str | None) -> str:
        return (value or "").strip().lower()

    def _matches_filters(
        self,
        item: dict,
        doc_type: str | None,
        campaign_name: str | None,
        channel: str | None,
        region: str | None,
        period_start: str | None,
        period_end: str | None,
    ) -> bool:
        if doc_type and self._normalize(item.get("doc_type")) != self._normalize(
            doc_type
        ):
            return False
        if campaign_name and self._normalize(campaign_name) not in self._normalize(
            item.get("campaign_name")
        ):
            return False
        if channel and self._normalize(item.get("channel")) != self._normalize(channel):
            return False
        if region and self._normalize(item.get("region")) != self._normalize(region):
            return False

        if period_start or period_end:
            filter_start = self._parse_dt(period_start)
            filter_end = self._parse_dt(period_end)
            doc_start = self._parse_dt(item.get("period_start"))
            doc_end = self._parse_dt(item.get("period_end"))
            if not doc_start and not doc_end:
                return False
            if filter_start and doc_end and doc_end < filter_start:
                return False
            if filter_end and doc_start and doc_start > filter_end:
                return False
        return True

    @staticmethod
    def _aggregate_metrics(items: list[dict]) -> dict[str, float]:
        totals = {
            "impressions": 0.0,
            "clicks": 0.0,
            "ctr": 0.0,
            "cvr": 0.0,
            "spend": 0.0,
            "roi": 0.0,
        }
        avg_fields = {"ctr", "cvr", "roi"}
        counts = {field: 0 for field in avg_fields}

        for item in items:
            metrics = item.get("metrics") or {}
            if not isinstance(metrics, dict):
                continue
            for key in totals:
                value = metrics.get(key)
                if isinstance(value, (int, float)):
                    totals[key] += float(value)
                    if key in avg_fields:
                        counts[key] += 1

        for field in avg_fields:
            if counts[field] > 0:
                totals[field] = totals[field] / counts[field]
            else:
                totals[field] = 0.0

        return totals

    def _build_report(
        self,
        query: str,
        items: list[dict],
        title: str | None,
        campaign_name: str | None,
        channel: str | None,
        region: str | None,
        period_start: str | None,
        period_end: str | None,
    ) -> dict[str, Any] | None:
        if not items:
            return None

        metrics = self._aggregate_metrics(items)
        tag_counts = Counter()
        source_counts = Counter()
        channel_counts = Counter()

        for item in items:
            tags = item.get("tags") or []
            if isinstance(tags, list):
                for tag in tags:
                    if isinstance(tag, str) and tag.strip():
                        tag_counts[tag.strip()] += 1
            source = item.get("source")
            if isinstance(source, str) and source.strip():
                source_counts[source.strip()] += 1
            ch = item.get("channel")
            if isinstance(ch, str) and ch.strip():
                channel_counts[ch.strip()] += 1

        top_tags = [tag for tag, _ in tag_counts.most_common(5)]
        top_sources = [src for src, _ in source_counts.most_common(3)]
        top_channels = [ch for ch, _ in channel_counts.most_common(3)]

        highlights = []
        for item in items[:5]:
            line = f"- {item.get('title', '')}"
            snippet = item.get("snippet") or ""
            if snippet:
                line += f": {snippet}"
            highlights.append(line)

        report_title = title or f"Daily Report - {query}"
        content_lines = [
            f"Query: {query}",
            f"Items: {len(items)}",
            f"Top Tags: {', '.join(top_tags) if top_tags else 'n/a'}",
            f"Top Sources: {', '.join(top_sources) if top_sources else 'n/a'}",
            f"Top Channels: {', '.join(top_channels) if top_channels else 'n/a'}",
            "Metrics Summary:",
            f"- impressions: {metrics.get('impressions', 0):.0f}",
            f"- clicks: {metrics.get('clicks', 0):.0f}",
            f"- ctr(avg): {metrics.get('ctr', 0):.4f}",
            f"- cvr(avg): {metrics.get('cvr', 0):.4f}",
            f"- spend: {metrics.get('spend', 0):.2f}",
            f"- roi(avg): {metrics.get('roi', 0):.4f}",
            "Highlights:",
            *highlights,
        ]
        content = "\n".join(content_lines).strip()

        return {
            "title": report_title,
            "content": content,
            "doc_type": "daily_report",
            "source": "daily_report",
            "campaign_name": campaign_name,
            "channel": channel,
            "region": region,
            "period_start": period_start,
            "period_end": period_end,
            "metrics": metrics,
            "tags": top_tags + [query],
        }
