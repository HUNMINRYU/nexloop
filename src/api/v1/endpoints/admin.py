from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from src.infrastructure.database.connection import get_db_session
from src.infrastructure.database.models import Role, Team, AuditLog, PipelineSchedule
from src.schemas.requests import RoleCreateRequest, TeamCreateRequest, ScheduleRequest
from src.schemas.responses import ScheduleResponse
from src.api.deps import require_role, CurrentUser, get_scheduler_client
from src.core.audit import record_audit_log
from src.utils.cache import clear_all_api_cache, get_cache_stats
from src.config.dependencies import get_services
from src.infrastructure.clients.scheduler_client import CloudSchedulerClient
from src.services.scheduler_service import SchedulerService
import os

router = APIRouter()


@router.get("/cache/stats")
async def get_cache_stats_endpoint(
    user: Annotated[CurrentUser, Depends(require_role(["admin"]))],
):
    return {"stats": get_cache_stats()}


@router.post("/cache/clear")
async def clear_cache_endpoint(
    user: Annotated[CurrentUser, Depends(require_role(["admin"]))],
):
    cleared = clear_all_api_cache()
    return {"cleared": cleared}


from src.services.admin_service import AdminService

# ... (Previous imports kept if needed, removing unused)
# Removing Models import for Role, Team, AuditLog direct usage


# Dependency
async def get_admin_service(
    session=Depends(get_db_session),
    scheduler_client: CloudSchedulerClient = Depends(get_scheduler_client),
) -> AdminService:
    services = get_services()
    return AdminService(session, scheduler_client, services.storage_service)


@router.get("/roles")
async def list_roles(
    user: Annotated[CurrentUser, Depends(require_role(["admin"]))],
    service: AdminService = Depends(get_admin_service),
):
    roles = await service.get_roles()
    return {
        "roles": [
            {"id": role.id, "name": role.name, "description": role.description}
            for role in roles
        ]
    }


@router.post("/roles")
async def create_role(
    request: RoleCreateRequest,
    user: Annotated[CurrentUser, Depends(require_role(["admin"]))],
    service: AdminService = Depends(get_admin_service),
):
    role = await service.create_role(
        name=request.name,
        description=request.description,
        actor_email=getattr(user, "email", "unknown"),
        actor_role=getattr(user, "role", "editor"),
    )
    return {"id": role.id, "name": role.name, "description": role.description}


@router.get("/teams")
async def list_teams(
    user: Annotated[CurrentUser, Depends(require_role(["admin"]))],
    service: AdminService = Depends(get_admin_service),
):
    teams = await service.get_teams()
    return {"teams": [{"id": team.id, "name": team.name} for team in teams]}


@router.post("/teams")
async def create_team(
    request: TeamCreateRequest,
    user: Annotated[CurrentUser, Depends(require_role(["admin"]))],
    service: AdminService = Depends(get_admin_service),
):
    team = await service.create_team(
        name=request.name,
        actor_email=getattr(user, "email", "unknown"),
        actor_role=getattr(user, "role", "editor"),
    )
    return {"id": team.id, "name": team.name}


@router.get("/audit-logs")
async def list_audit_logs(
    user: Annotated[CurrentUser, Depends(require_role(["admin"]))],
    limit: int = 50,
    service: AdminService = Depends(get_admin_service),
):
    logs = await service.get_audit_logs(limit=limit)
    return {
        "logs": [
            {
                "id": log.id,
                "action": log.action,
                "actor_email": log.actor_email,
                "actor_role": log.actor_role,
                "entity_type": log.entity_type,
                "entity_id": log.entity_id,
                "metadata": log.meta_json,
                "created_at": log.created_at.isoformat() if log.created_at else None,
            }
            for log in logs
        ]
    }


@router.get("/gcs/metadata")
async def get_gcs_metadata(
    user: Annotated[CurrentUser, Depends(require_role(["admin"]))],
    gcs_path: str | None = None,
    prefix: str | None = None,
    limit: int = 50,
):
    services = get_services()
    storage = services.storage_service
    bucket_name = storage.bucket_name

    if not gcs_path and not prefix:
        raise HTTPException(
            status_code=400, detail="gcs_path 또는 prefix가 필요합니다."
        )

    def _parse_gcs_path(raw: str) -> tuple[str | None, str]:
        raw = raw.strip()
        if raw.startswith("gs://"):
            parts = raw[5:].split("/", 1)
            bucket = parts[0]
            object_path = parts[1] if len(parts) == 2 else ""
            return bucket, object_path
        return None, raw.lstrip("/")

    if gcs_path:
        bucket, object_path = _parse_gcs_path(gcs_path)
        if bucket and bucket_name and bucket != bucket_name:
            raise HTTPException(status_code=400, detail="Bucket mismatch")
        metadata = storage.get_metadata(object_path)
        if not metadata:
            raise HTTPException(status_code=404, detail="Object not found")
        url = getattr(storage, "get_signed_url", lambda p: None)(object_path)
        return {"items": [{**metadata, "signed_url": url}]}

    bucket, object_prefix = _parse_gcs_path(prefix or "")
    if bucket and bucket_name and bucket != bucket_name:
        raise HTTPException(status_code=400, detail="Bucket mismatch")

    paths = storage.list_files(object_prefix)[: max(1, min(limit, 200))]
    items = []
    for path in paths:
        metadata = storage.get_metadata(path)
        if not metadata:
            continue
        url = getattr(storage, "get_signed_url", lambda p: None)(path)
        items.append({**metadata, "signed_url": url})
    return {"items": items}


@router.get("/prompt-logs")
async def get_prompt_logs(
    user: Annotated[CurrentUser, Depends(require_role(["admin"]))], limit: int = 20
):
    services = get_services()
    history = services.history_service.get_history_list()
    logs = []
    for item in history[: max(1, min(limit, 50))]:
        record = services.history_service.load_history(item.get("id", ""))
        prompt_log = getattr(record, "prompt_log", None) if record else None
        logs.append(
            {
                "history_id": item.get("id"),
                "product_name": item.get("product_name", ""),
                "executed_at": item.get("executed_at", ""),
                "prompt_log": prompt_log,
            }
        )
    return {"logs": logs}


# 스케줄 목록 조회
@router.get("/schedules", response_model=list[ScheduleResponse])
async def list_schedules(
    user: Annotated[CurrentUser, Depends(require_role(["admin"]))],
    session=Depends(get_db_session),
):
    """스케줄 목록 조회"""
    result = await session.execute(
        select(PipelineSchedule)
        .where(PipelineSchedule.deleted_at.is_(None))
        .order_by(PipelineSchedule.id.desc())
    )
    schedules = result.scalars().all()
    return [ScheduleResponse.model_validate(s) for s in schedules]


# 스케줄 생성
@router.post("/schedules", response_model=ScheduleResponse)
async def create_schedule(
    request: ScheduleRequest,
    user: Annotated[CurrentUser, Depends(require_role(["admin"]))],
    session=Depends(get_db_session),
    scheduler_client: CloudSchedulerClient = Depends(get_scheduler_client),
):
    """스케줄 생성"""
    service = SchedulerService(session, scheduler_client)
    try:
        schedule = service.create_schedule(request, user.id)
        await record_audit_log(
            session=session,
            action="create_schedule",
            actor_email=user.email,
            actor_role=user.role,
            entity_type="schedule",
            entity_id=str(schedule.id),
            metadata={"name": schedule.name, "product": schedule.product_name},
        )
        return ScheduleResponse.model_validate(schedule)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e


# 스케줄 수정
@router.put("/schedules/{schedule_id}", response_model=ScheduleResponse)
async def update_schedule(
    schedule_id: int,
    request: ScheduleRequest,
    user: Annotated[CurrentUser, Depends(require_role(["admin"]))],
    session=Depends(get_db_session),
    scheduler_client: CloudSchedulerClient = Depends(get_scheduler_client),
):
    """스케줄 수정"""
    service = SchedulerService(session, scheduler_client)
    try:
        schedule = service.update_schedule(schedule_id, request)
        await record_audit_log(
            session=session,
            action="update_schedule",
            actor_email=user.email,
            actor_role=user.role,
            entity_type="schedule",
            entity_id=str(schedule.id),
            metadata={"name": schedule.name},
        )
        return ScheduleResponse.model_validate(schedule)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e


# 스케줄 삭제
@router.delete("/schedules/{schedule_id}")
async def delete_schedule(
    schedule_id: int,
    user: Annotated[CurrentUser, Depends(require_role(["admin"]))],
    session=Depends(get_db_session),
    scheduler_client: CloudSchedulerClient = Depends(get_scheduler_client),
):
    """스케줄 삭제"""
    service = SchedulerService(session, scheduler_client)
    try:
        service.delete_schedule(schedule_id)
        await record_audit_log(
            session=session,
            action="delete_schedule",
            actor_email=user.email,
            actor_role=user.role,
            entity_type="schedule",
            entity_id=str(schedule_id),
            metadata={},
        )
        return {"message": "Schedule deleted"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e


# 스케줄 활성화/비활성화
@router.patch("/schedules/{schedule_id}/toggle")
async def toggle_schedule(
    schedule_id: int,
    enabled: bool,
    user: Annotated[CurrentUser, Depends(require_role(["admin"]))],
    session=Depends(get_db_session),
    scheduler_client: CloudSchedulerClient = Depends(get_scheduler_client),
):
    """스케줄 활성화/비활성화"""
    service = SchedulerService(session, scheduler_client)
    try:
        service.toggle_schedule(schedule_id, enabled)
        await record_audit_log(
            session=session,
            action="toggle_schedule",
            actor_email=user.email,
            actor_role=user.role,
            entity_type="schedule",
            entity_id=str(schedule_id),
            metadata={"enabled": enabled},
        )
        return {"message": f"Schedule {'enabled' if enabled else 'disabled'}"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
