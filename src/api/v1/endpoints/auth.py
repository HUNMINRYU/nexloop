from fastapi import APIRouter, Depends
from schemas.requests import AuthLoginRequest, AuthSignupRequest
from infrastructure.database.connection import get_db_session
from config.dependencies import get_services

router = APIRouter()


@router.post("/signup")
async def signup(request: AuthSignupRequest, session=Depends(get_db_session)):
    services = get_services()
    if request.name:
        name = request.name
    else:
        name = request.email.split("@")[0] if "@" in request.email else "user"
    return await services.auth_service.signup(
        session=session,
        name=name,
        email=request.email,
        password=request.password,
        team_name=request.team_name,
        job_title=request.job_title,
        phone_number=request.phone_number,
    )


@router.post("/login")
async def login(request: AuthLoginRequest, session=Depends(get_db_session)):
    services = get_services()
    return await services.auth_service.login(
        session=session,
        email=request.email,
        password=request.password,
    )
