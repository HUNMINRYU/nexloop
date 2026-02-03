import asyncio
import json
from datetime import datetime, timedelta, timezone
from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func, select

from api.deps import CurrentUser, require_role
from config.dependencies import get_services
from config.settings import get_settings
from core.audit import record_audit_log
from infrastructure.database.connection import get_db_session
from infrastructure.database.models import AuditLog, Team, User
from schemas.requests import (
    DailyReportRequest,
    InsightUploadRequest,
    NaverInsightBatchRequest,
)

router = APIRouter()


@router.post("/insights/upload")
async def upload_insights(
    request: InsightUploadRequest,
    user: Annotated[CurrentUser, Depends(require_role(["admin", "editor"]))],
    session: Annotated[Any, Depends(get_db_session)],
):
    if not request.items:
        raise HTTPException(status_code=400, detail="items required")

    services = get_services()
    try:
        ingested = await asyncio.to_thread(
            services.rag_ingestion_service.ingest_manual_upload,
            request.items,
            user,
        )
    except Exception as exc:
        await record_audit_log(
            session=session,
            action="insights.manual_upload_failed",
            actor_email=getattr(user, "email", "unknown"),
            actor_role=getattr(user, "role", "editor"),
            entity_type="insight",
            metadata={
                "items": len(request.items),
                "error": str(exc),
            },
        )
        raise HTTPException(status_code=500, detail="Manual upload failed.") from exc
    await record_audit_log(
        session=session,
        action="insights.manual_upload",
        actor_email=getattr(user, "email", "unknown"),
        actor_role=getattr(user, "role", "editor"),
        entity_type="insight",
        metadata={
            "items": len(request.items),
            "ingested": ingested,
        },
    )
    if ingested == 0 and request.items:
        await record_audit_log(
            session=session,
            action="insights.manual_upload_failed",
            actor_email=getattr(user, "email", "unknown"),
            actor_role=getattr(user, "role", "editor"),
            entity_type="insight",
            metadata={
                "items": len(request.items),
                "ingested": ingested,
                "reason": "ingested_zero",
            },
        )
    return {"ingested": ingested, "items": len(request.items)}


@router.post("/insights/external/naver")
async def ingest_naver_insights(
    request: NaverInsightBatchRequest,
    user: Annotated[CurrentUser, Depends(require_role(["admin", "editor"]))],
    session: Annotated[Any, Depends(get_db_session)],
):
    services = get_services()
    meta = {
        "campaign_name": request.campaign_name,
        "channel": request.channel,
        "region": request.region,
        "period_start": request.period_start,
        "period_end": request.period_end,
    }
    try:
        result = await asyncio.to_thread(
            services.insight_external_service.ingest_naver,
            request.query,
            request.max_results,
            request.include_products,
            request.include_blogs,
            request.include_news,
            meta,
            user,
        )
    except Exception as exc:
        await record_audit_log(
            session=session,
            action="insights.naver_ingest_failed",
            actor_email=getattr(user, "email", "unknown"),
            actor_role=getattr(user, "role", "editor"),
            entity_type="insight",
            metadata={
                "query": request.query,
                "error": str(exc),
            },
        )
        raise HTTPException(status_code=500, detail="Naver ingest failed.") from exc
    await record_audit_log(
        session=session,
        action="insights.naver_ingest",
        actor_email=getattr(user, "email", "unknown"),
        actor_role=getattr(user, "role", "editor"),
        entity_type="insight",
        metadata={
            "query": request.query,
            "items": result.get("items"),
            "ingested": result.get("ingested"),
            "products": result.get("products"),
            "blogs": result.get("blogs"),
            "news": result.get("news"),
        },
    )
    if (result.get("items", 0) or 0) > 0 and (result.get("ingested", 0) or 0) == 0:
        await record_audit_log(
            session=session,
            action="insights.naver_ingest_failed",
            actor_email=getattr(user, "email", "unknown"),
            actor_role=getattr(user, "role", "editor"),
            entity_type="insight",
            metadata={
                "query": request.query,
                "items": result.get("items"),
                "ingested": result.get("ingested"),
                "reason": "ingested_zero",
            },
        )
    return result


def _parse_dt(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None


def _normalize(value: str | None) -> str:
    return (value or "").strip().lower()


def _matches_filters(
    item: dict,
    doc_type: str | None,
    campaign_name: str | None,
    channel: str | None,
    region: str | None,
    period_start: str | None,
    period_end: str | None,
) -> bool:
    if doc_type and _normalize(item.get("doc_type")) != _normalize(doc_type):
        return False
    if campaign_name and _normalize(campaign_name) not in _normalize(
        item.get("campaign_name")
    ):
        return False
    if channel and _normalize(item.get("channel")) != _normalize(channel):
        return False
    if region and _normalize(item.get("region")) != _normalize(region):
        return False

    if period_start or period_end:
        filter_start = _parse_dt(period_start)
        filter_end = _parse_dt(period_end)
        doc_start = _parse_dt(item.get("period_start"))
        doc_end = _parse_dt(item.get("period_end"))
        if not doc_start and not doc_end:
            return False
        if filter_start and doc_end and doc_end < filter_start:
            return False
        if filter_end and doc_start and doc_start > filter_end:
            return False
    return True


@router.get("/insights/search")
async def search_insights(
    q: str,
    user: CurrentUser,
    session: Annotated[Any, Depends(get_db_session)],
    max_results: int = 20,
    doc_type: str | None = None,
    campaign_name: str | None = None,
    channel: str | None = None,
    region: str | None = None,
    period_start: str | None = None,
    period_end: str | None = None,
):
    services = get_services()
    settings = get_settings()
    data_store_id = settings.rag_data_stores.get(getattr(user, "role", ""))

    limit = max(1, min(int(max_results), 50))
    results = services.discovery_engine_client.search(
        q,
        max_results=limit,
        data_store_id=data_store_id,
    )

    filtered = [
        item
        for item in results
        if _matches_filters(
            item,
            doc_type,
            campaign_name,
            channel,
            region,
            period_start,
            period_end,
        )
    ]

    await record_audit_log(
        session=session,
        action="insights.search",
        actor_email=getattr(user, "email", "unknown"),
        actor_role=getattr(user, "role", "viewer"),
        entity_type="insight",
        metadata={
            "query": q,
            "count": len(filtered),
            "filters": {
                "doc_type": doc_type,
                "campaign_name": campaign_name,
                "channel": channel,
                "region": region,
                "period_start": period_start,
                "period_end": period_end,
            },
        },
    )
    return {"query": q, "results": filtered, "count": len(filtered)}


@router.get("/insights/metrics")
async def insights_metrics(
    user: Annotated[CurrentUser, Depends(require_role(["admin", "editor"]))],
    session: Annotated[Any, Depends(get_db_session)],
    days: int = 7,
    actor_role: str | None = None,
    team_id: int | None = None,
    team_name: str | None = None,
):
    window_days = max(1, min(int(days), 90))
    cutoff = datetime.now(timezone.utc) - timedelta(days=window_days)
    stmt = (
        select(
            AuditLog.action,
            func.count(AuditLog.id),
            func.max(AuditLog.created_at),
        )
        .select_from(AuditLog)
        .outerjoin(User, User.email == AuditLog.actor_email)
        .outerjoin(Team, Team.id == User.team_id)
        .where(AuditLog.entity_type == "insight")
        .where(AuditLog.created_at >= cutoff)
    )
    if actor_role:
        stmt = stmt.where(AuditLog.actor_role == actor_role.strip().lower())
    if team_id:
        stmt = stmt.where(Team.id == team_id)
    if team_name:
        stmt = stmt.where(Team.name == team_name.strip())
    stmt = stmt.group_by(AuditLog.action)
    rows = (await session.execute(stmt)).all()
    by_action = [
        {
            "action": action,
            "count": int(count or 0),
            "last_seen": last.isoformat() if last else None,
        }
        for action, count, last in rows
    ]
    total = sum(item["count"] for item in by_action)
    return {
        "window_days": window_days,
        "total": total,
        "by_action": by_action,
    }


@router.get("/insights/teams")
async def insights_teams(
    user: Annotated[CurrentUser, Depends(require_role(["admin", "editor"]))],
    session: Annotated[Any, Depends(get_db_session)],
):
    result = await session.execute(select(Team))
    teams = result.scalars().all()
    return {"teams": [{"id": team.id, "name": team.name} for team in teams]}


@router.get("/insights/failures")
async def insights_failures(
    user: Annotated[CurrentUser, Depends(require_role(["admin", "editor"]))],
    session: Annotated[Any, Depends(get_db_session)],
    days: int = 7,
    limit: int = 50,
    actor_role: str | None = None,
    team_id: int | None = None,
    team_name: str | None = None,
):
    window_days = max(1, min(int(days), 90))
    row_limit = max(1, min(int(limit), 200))
    cutoff = datetime.now(timezone.utc) - timedelta(days=window_days)
    stmt = (
        select(AuditLog, Team.id, Team.name)
        .select_from(AuditLog)
        .outerjoin(User, User.email == AuditLog.actor_email)
        .outerjoin(Team, Team.id == User.team_id)
        .where(AuditLog.entity_type == "insight")
        .where(AuditLog.action.like("insights.%_failed"))
        .where(AuditLog.created_at >= cutoff)
    )
    if actor_role:
        stmt = stmt.where(AuditLog.actor_role == actor_role.strip().lower())
    if team_id:
        stmt = stmt.where(Team.id == team_id)
    if team_name:
        stmt = stmt.where(Team.name == team_name.strip())
    stmt = stmt.order_by(AuditLog.created_at.desc()).limit(row_limit)
    rows = (await session.execute(stmt)).all()
    items = []
    for log, team_id_value, team_name_value in rows:
        metadata = None
        if log.meta_json:
            try:
                metadata = json.loads(log.meta_json)
            except Exception:
                metadata = {"raw": log.meta_json}
        items.append(
            {
                "id": log.id,
                "action": log.action,
                "actor_email": log.actor_email,
                "actor_role": log.actor_role,
                "entity_id": log.entity_id,
                "actor_team": (
                    {"id": team_id_value, "name": team_name_value}
                    if team_id_value
                    else None
                ),
                "metadata": metadata,
                "created_at": log.created_at.isoformat(),
            }
        )
    return {
        "window_days": window_days,
        "items": items,
    }


@router.post("/insights/reports/daily")
async def generate_daily_report(
    request: DailyReportRequest,
    user: Annotated[CurrentUser, Depends(require_role(["admin", "editor"]))],
    session: Annotated[Any, Depends(get_db_session)],
):
    services = get_services()
    settings = get_settings()
    data_store_id = settings.rag_data_stores.get(getattr(user, "role", ""))

    try:
        result = await asyncio.to_thread(
            services.insight_report_service.generate_daily_report,
            request.query,
            request.max_results,
            data_store_id,
            request.doc_type,
            request.campaign_name,
            request.channel,
            request.region,
            request.period_start,
            request.period_end,
            request.title,
            user,
        )
    except Exception as exc:
        await record_audit_log(
            session=session,
            action="insights.daily_report_failed",
            actor_email=getattr(user, "email", "unknown"),
            actor_role=getattr(user, "role", "editor"),
            entity_type="insight",
            metadata={
                "query": request.query,
                "error": str(exc),
            },
        )
        raise HTTPException(status_code=500, detail="Daily report failed.") from exc
    await record_audit_log(
        session=session,
        action="insights.daily_report",
        actor_email=getattr(user, "email", "unknown"),
        actor_role=getattr(user, "role", "editor"),
        entity_type="insight",
        metadata={
            "query": request.query,
            "items": result.get("items"),
            "ingested": result.get("ingested"),
        },
    )
    if (result.get("items", 0) or 0) > 0 and (result.get("ingested", 0) or 0) == 0:
        await record_audit_log(
            session=session,
            action="insights.daily_report_failed",
            actor_email=getattr(user, "email", "unknown"),
            actor_role=getattr(user, "role", "editor"),
            entity_type="insight",
            metadata={
                "query": request.query,
                "items": result.get("items"),
                "ingested": result.get("ingested"),
                "reason": "ingested_zero",
            },
        )
    return result
