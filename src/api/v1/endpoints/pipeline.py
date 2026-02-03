import asyncio
import json
from datetime import datetime
from typing import Annotated, Any
from uuid import uuid4

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from fastapi.responses import StreamingResponse

from api.deps import CurrentUser, require_role
from config.dependencies import get_services
from config.products import get_product_by_name
from core.audit import record_audit_log
from core.state import PIPELINE_RESULTS, PIPELINE_STATUS
from infrastructure.database.connection import get_db_session
from schemas.requests import (
    AnalysisTaskRequest,
    ApprovalStatusRequest,
    CTRPredictRequest,
    NotionExportRequest,
    PipelineRequest,
)
from services.pipeline_runner import execute_pipeline_task, init_pipeline_status

# from utils.file_store import ensure_output_dir  <-- keeping if used later, but it was used in update_status endpoint fallback
from utils.file_store import ensure_output_dir

router = APIRouter()


def _get_task_status_and_result(task_id: str) -> tuple[dict[str, Any], dict[str, Any]]:
    status = PIPELINE_STATUS.get(task_id)
    result = PIPELINE_RESULTS.get(task_id)
    if not status:
        raise HTTPException(status_code=404, detail="Task not found")
    if not result:
        raise HTTPException(status_code=404, detail="Task result not found")
    return status, result


def _extract_collected_data(result: dict[str, Any]) -> dict[str, Any]:
    collected = result.get("collected_data") or {}
    return collected if isinstance(collected, dict) else {}


@router.get("/history")
async def get_pipeline_history(user: CurrentUser):
    services = get_services()
    history_items = services.history_service.get_history_list()

    history_tasks = []
    for item in history_items:
        executed_at = item.get("executed_at", "")
        history_tasks.append(
            {
                "task_id": item.get("id"),
                "product": item.get("product_name", ""),
                "status": "success" if item.get("success") else "failed",
                "created_at": executed_at,
                "updated_at": executed_at,
            }
        )

    in_memory_tasks = [
        {
            "task_id": task.get("task_id"),
            "product": task.get("product"),
            "status": task.get("status"),
            "created_at": task.get("created_at"),
            "updated_at": task.get("updated_at"),
        }
        for task in PIPELINE_STATUS.values()
    ]

    tasks_by_id = {
        task["task_id"]: task for task in in_memory_tasks if task.get("task_id")
    }
    for task in history_tasks:
        task_id = task.get("task_id")
        if task_id and task_id not in tasks_by_id:
            tasks_by_id[task_id] = task

    tasks = list(tasks_by_id.values())
    tasks.sort(key=lambda item: item.get("updated_at") or "", reverse=True)
    return {"tasks": tasks}


@router.get("/status/{task_id}")
async def get_pipeline_status(task_id: str):
    status = PIPELINE_STATUS.get(task_id)
    if not status:
        raise HTTPException(status_code=404, detail="Task not found")
    return status


@router.get("/status-stream/{task_id}")
async def stream_pipeline_status(task_id: str):
    async def event_generator():
        while True:
            status = PIPELINE_STATUS.get(task_id)
            if not status:
                yield "event: error\ndata: {}\n\n"
                break
            yield f"data: {json.dumps(status)}\n\n"
            if status.get("status") in {"success", "failed"}:
                break
            await asyncio.sleep(1)

    return StreamingResponse(event_generator(), media_type="text/event-stream")


@router.get("/result/{task_id}")
async def get_pipeline_result(task_id: str, user: CurrentUser):
    status = PIPELINE_STATUS.get(task_id)
    result = PIPELINE_RESULTS.get(task_id)
    if not status:
        services = get_services()
        history_record = services.history_service.load_history(task_id)
        if history_record:
            record_data = history_record.model_dump()
            return {
                "status": {
                    "task_id": task_id,
                    "status": "success" if record_data.get("success") else "failed",
                    "product": record_data.get("product_name", ""),
                    "message": "히스토리 결과",
                    "progress": {
                        "message": "히스토리 로드",
                        "percentage": 100 if record_data.get("success") else 0,
                        "step": "completed" if record_data.get("success") else "failed",
                    },
                    "created_at": record_data.get("executed_at", ""),
                    "updated_at": record_data.get("executed_at", ""),
                },
                "result": record_data,
            }
        raise HTTPException(status_code=404, detail="Task not found")
    return {
        "status": status,
        "result": result,
    }


@router.post("/run")
async def trigger_pipeline(
    request: PipelineRequest,
    background_tasks: BackgroundTasks,
    user: CurrentUser,
):
    product = get_product_by_name(request.product_name)
    if not product:
        raise HTTPException(
            status_code=404, detail=f"Product '{request.product_name}' not found"
        )

    task_id = str(uuid4())
    init_pipeline_status(task_id, request.product_name)
    background_tasks.add_task(execute_pipeline_task, request, task_id)

    return {
        "status": "triggered",
        "task_id": task_id,
        "product": request.product_name,
        "timestamp": datetime.now().isoformat(),
    }


@router.patch("/result/{task_id}/status")
async def update_pipeline_status_endpoint(
    task_id: str,
    request: ApprovalStatusRequest,
    user: Annotated[CurrentUser, Depends(require_role(["admin", "approver"]))],
    session: Annotated[Any, Depends(get_db_session)],
):
    allowed = {"draft", "pending_review", "approved", "rejected"}
    if request.status not in allowed:
        raise HTTPException(status_code=400, detail="Invalid status")

    def _append_audit(result_obj: dict[str, Any]) -> None:
        trail = result_obj.get("audit_trail")
        if not isinstance(trail, list):
            trail = []
        trail.append(
            {
                "action": f"status:{request.status}",
                "by": getattr(user, "email", "unknown"),
                "at": datetime.now().isoformat(),
            }
        )
        result_obj["audit_trail"] = trail

    if task_id in PIPELINE_RESULTS:
        result = PIPELINE_RESULTS[task_id]
        result["approval_status"] = request.status
        _append_audit(result)
        PIPELINE_RESULTS[task_id] = result
        await record_audit_log(
            session=session,
            action="update_approval_status",
            actor_email=getattr(user, "email", "unknown"),
            actor_role=getattr(user, "role", "editor"),
            entity_type="pipeline_result",
            entity_id=str(task_id),
            metadata={"status": request.status},
        )
        return {"status": request.status}

    meta_dir = ensure_output_dir() / "metadata"
    file_path = meta_dir / f"{task_id}.json"
    if file_path.exists():
        try:
            data = json.loads(file_path.read_text(encoding="utf-8"))
            data["approval_status"] = request.status
            _append_audit(data)
            file_path.write_text(
                json.dumps(data, ensure_ascii=False, indent=2),
                encoding="utf-8",
            )
            await record_audit_log(
                session=session,
                action="update_approval_status",
                actor_email=getattr(user, "email", "unknown"),
                actor_role=getattr(user, "role", "editor"),
                entity_type="pipeline_result",
                entity_id=str(task_id),
                metadata={"status": request.status},
            )
            return {"status": request.status}
        except Exception as e:
            raise HTTPException(
                status_code=500, detail="Failed to update history"
            ) from e

    raise HTTPException(status_code=404, detail="Task not found")


@router.post("/analysis/strategy")
async def analyze_strategy(request: AnalysisTaskRequest):
    services = get_services()
    status, result = _get_task_status_and_result(request.task_id)
    strategy = result.get("strategy")
    if strategy:
        return {"strategy": strategy}

    collected = _extract_collected_data(result)
    youtube_data = collected.get("youtube_data", {})
    naver_data = collected.get("naver_data", {})
    top_insights = collected.get("top_insights", [])
    product_name = status.get("product") or result.get("product_name", "")
    if not product_name:
        raise HTTPException(status_code=400, detail="Product name not found")

    services.marketing_service.analyze_data(
        youtube_data=youtube_data,
        naver_data=naver_data,
        product_name=product_name,
        top_insights=top_insights,
    )
    if request.task_id in PIPELINE_RESULTS:
        PIPELINE_RESULTS[request.task_id]["strategy"] = strategy
    return {"strategy": strategy}


@router.post("/analysis/comments/basic")
async def analyze_comments_basic(request: AnalysisTaskRequest):
    services = get_services()
    _, result = _get_task_status_and_result(request.task_id)
    collected = _extract_collected_data(result)
    youtube_data = collected.get("youtube_data", {})
    comments = youtube_data.get("comments", [])
    if not comments:
        raise HTTPException(status_code=400, detail="No comments available")
    analysis = services.comment_analysis_service.analyze_comments(comments)
    return {"analysis": analysis}


@router.post("/analysis/comments/deep")
async def analyze_comments_deep(request: AnalysisTaskRequest):
    services = get_services()
    _, result = _get_task_status_and_result(request.task_id)
    collected = _extract_collected_data(result)
    youtube_data = collected.get("youtube_data", {})
    comments = youtube_data.get("comments", [])
    if not comments:
        raise HTTPException(status_code=400, detail="No comments available")
    analysis = services.comment_analysis_service.analyze_with_ai(comments)
    return {"analysis": analysis}


@router.post("/analysis/ctr-predict")
async def predict_ctr(request: CTRPredictRequest):
    services = get_services()
    _, result = _get_task_status_and_result(request.task_id)
    collected = _extract_collected_data(result)
    top_insights = collected.get("top_insights", [])
    try:
        ai_prediction = await services.ctr_predictor.predict_with_ai(
            title=request.title,
            category="marketing",
            top_insights=top_insights,
        )
    except Exception:
        ai_prediction = services.ctr_predictor.predict_ctr(
            title=request.title,
            thumbnail_description=request.thumbnail_description,
            competitor_titles=request.competitor_titles,
        )

    basic = services.ctr_predictor.predict_ctr(
        title=request.title,
        thumbnail_description=request.thumbnail_description,
        competitor_titles=request.competitor_titles,
    )
    ai_prediction.update(
        {
            "breakdown": basic.get("breakdown", {}),
            "total_score": basic.get("total_score", 0),
            "predicted_ctr": basic.get("predicted_ctr", 0),
            "grade": basic.get("grade", "C"),
            "ctr_range": basic.get("ctr_range", ""),
        }
    )
    return {"prediction": ai_prediction}


@router.post("/export/notion")
async def export_notion(request: NotionExportRequest, user: CurrentUser):
    if not request.task_id and not request.history_id:
        raise HTTPException(
            status_code=400, detail="task_id 또는 history_id가 필요합니다."
        )

    services = get_services()
    result = None
    if request.task_id:
        try:
            _, result = _get_task_status_and_result(request.task_id)
        except HTTPException:
            result = None

    if result is None and request.history_id:
        record = services.history_service.load_history(request.history_id)
        if record:
            result = record.model_dump()

    if result is None:
        raise HTTPException(status_code=404, detail="Task result not found")

    product_name = result.get("product_name", "")
    product = get_product_by_name(product_name)
    product_dict = (
        (
            product.model_dump()
            if product and hasattr(product, "model_dump")
            else product.__dict__
        )
        if product
        else {"name": product_name}
    )
    collected = result.get("collected_data") or {}
    strategy = result.get("strategy") or {}
    top_insights = collected.get("top_insights") if isinstance(collected, dict) else []

    export_data = {
        "product": product_dict,
        "analysis": {
            "summary": strategy.get("summary", ""),
            "target_audience": strategy.get("target_audience", {}),
            "hook_suggestions": strategy.get("hook_suggestions", []),
            "competitor_analysis": strategy.get("competitor_analysis", {}),
            "unique_selling_point": strategy.get("unique_selling_point", []),
            "insights": [
                item.get("content", "")
                for item in (top_insights or [])
                if isinstance(item, dict)
            ],
        },
    }

    notion_url = services.export_service.export_notion(
        export_data,
        parent_page_id=request.parent_page_id,
    )
    return {"url": notion_url}
