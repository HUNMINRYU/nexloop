from typing import Annotated, Any

from fastapi import Depends, Header, HTTPException

from config.dependencies import get_services
from infrastructure.database.connection import get_db_session


async def get_current_user(
    session: Annotated[Any, Depends(get_db_session)],
    authorization: Annotated[str | None, Header()] = None,
):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Authorization required")
    token = authorization.split(" ", 1)[1].strip()
    services = get_services()
    return await services.auth_service.get_current_user(session, token)


CurrentUser = Annotated[Any, Depends(get_current_user)]


async def get_current_user_optional(
    session: Annotated[Any, Depends(get_db_session)],
    authorization: Annotated[str | None, Header()] = None,
):
    """
    Optional authentication dependency.
    Returns user if authenticated, None otherwise (no exception raised).
    """
    if not authorization or not authorization.startswith("Bearer "):
        return None
    token = authorization.split(" ", 1)[1].strip()
    services = get_services()
    try:
        return await services.auth_service.get_current_user(session, token)
    except Exception:
        return None


OptionalUser = Annotated[Any | None, Depends(get_current_user_optional)]


def require_role(roles: list[str]):
    async def _checker(user: CurrentUser):
        user_role = getattr(user, "role", "editor")
        if user_role not in roles:
            raise HTTPException(status_code=403, detail="Forbidden")
        return user

    return _checker


# Dependency for CloudSchedulerClient
def get_scheduler_client() -> "CloudSchedulerClient":
    """CloudSchedulerClient 의존성 주입"""
    import os
    from src.infrastructure.clients.scheduler_client import CloudSchedulerClient

    project_id = os.getenv("GOOGLE_CLOUD_PROJECT_ID")
    location = os.getenv("GOOGLE_CLOUD_LOCATION", "asia-northeast3")
    if not project_id:
        raise HTTPException(
            status_code=500,
            detail="GOOGLE_CLOUD_PROJECT_ID 환경 변수가 설정되지 않았습니다.",
        )
    return CloudSchedulerClient(project_id, location)
