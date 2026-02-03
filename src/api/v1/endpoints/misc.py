import json
from datetime import datetime
from fastapi import APIRouter, BackgroundTasks, HTTPException, Request
from api.deps import CurrentUser, OptionalUser
from config.dependencies import get_services
from config.settings import get_settings
from utils.file_store import ensure_output_dir
from utils.rate_limit import check_rate_limit, get_remaining_requests
from schemas.requests import LeadRequest, ChatRequest, RefreshUrlRequest

router = APIRouter()


@router.get("/health")
async def health_check():
    return {"status": "ok", "message": "Nexloop API is running"}


@router.post("/leads")
async def create_lead(request: LeadRequest):
    if "@" not in request.email:
        raise HTTPException(status_code=400, detail="Invalid email")
    out_dir = ensure_output_dir()
    lead_path = out_dir / "leads.jsonl"
    payload = {
        "email": request.email,
        "created_at": datetime.now().isoformat(),
    }
    with open(lead_path, "a", encoding="utf-8") as f:
        f.write(json.dumps(payload, ensure_ascii=False) + "\n")
    return {"status": "ok"}


@router.post("/chat")
async def chat(
    chat_request: ChatRequest,
    http_request: Request,
    user: OptionalUser = None,
):
    """
    Chat endpoint with optional authentication.
    - Authenticated users: unlimited access with role-based data store
    - Non-authenticated users: limited to 3 requests per IP with guest data store
    """
    services = get_services()
    settings = get_settings()

    # Get client IP address
    client_ip = http_request.client.host if http_request.client else "unknown"
    forwarded_for = http_request.headers.get("X-Forwarded-For")
    if forwarded_for:
        client_ip = forwarded_for.split(",")[0].strip()

    if user is None:
        # Non-authenticated user - apply rate limiting
        if not check_rate_limit(client_ip, max_requests=3):
            remaining = get_remaining_requests(client_ip, max_requests=3)
            raise HTTPException(
                status_code=429,
                detail=f"Rate limit exceeded. {remaining} requests remaining.",
            )

        # Use guest data store for non-authenticated users
        data_store_id = settings.rag_data_stores.get("guest")
        if not data_store_id:
            # Fallback to default data store if guest not configured
            data_store_id = settings.rag_data_stores.get("editor")
    else:
        # Authenticated user - use role-based data store
        data_store_id = settings.rag_data_stores.get(getattr(user, "role", "editor"))

    reply = services.chatbot_service.generate_reply(
        message=chat_request.message,
        session_id=chat_request.session_id or "",
        data_store_id=data_store_id,
    )
    return reply


@router.post("/refresh-url")
async def refresh_signed_url(request: RefreshUrlRequest):
    services = get_services()
    storage = services.storage_service

    raw_path = request.gcs_path.strip()
    path = raw_path
    if raw_path.startswith("gs://"):
        parts = raw_path[5:].split("/", 1)
        if len(parts) == 2:
            path = parts[1]
    url = storage.get_signed_url(path)
    if not url:
        raise HTTPException(status_code=404, detail="Failed to generate signed URL")
    return {"url": url}


@router.get("/search/discovery")
async def search_discovery(
    q: str,
    user: CurrentUser,
    background_tasks: BackgroundTasks,
    max_results: int = 5,
):
    services = get_services()
    settings = get_settings()
    data_store_id = settings.rag_data_stores.get(getattr(user, "role", ""))
    results = services.discovery_engine_client.search(
        q,
        max_results=max_results,
        data_store_id=data_store_id,
    )
    background_tasks.add_task(
        services.rag_ingestion_service.ingest_search_log,
        q,
        results,
        user,
    )
    return {"results": results}
