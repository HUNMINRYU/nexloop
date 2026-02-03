"""Webhook 엔드포인트

Cloud Scheduler와 같은 외부 서비스에서 호출하는 엔드포인트입니다.
인증이 필요 없으므로 주의해서 사용해야 합니다.
"""

from datetime import datetime
from uuid import uuid4

from fastapi import APIRouter, BackgroundTasks, Request, Depends
from sqlalchemy import select

from infrastructure.database.connection import get_db_session
from infrastructure.database.models import PipelineSchedule
from schemas.requests import PipelineRequest
from services.pipeline_runner import execute_pipeline_task, init_pipeline_status

router = APIRouter(prefix="/webhooks", tags=["Webhooks"])


@router.post("/scheduler")
async def scheduler_webhook(
    request: Request,
    background_tasks: BackgroundTasks,
    session=Depends(get_db_session),
):
    """Cloud Scheduler에서 호출하는 Webhook

    Cloud Scheduler Job이 실행될 때 이 엔드포인트를 호출하여 파이프라인을 실행합니다.
    인증이 필요 없으므로 외부에서 접근 가능합니다.

    요청 본문:
        - schedule_id: 스케줄 ID (선택)
        - product_name: 제품명 (필수)
        - 기타 PipelineRequest 파라미터들
    """
    # 요청 본문 파싱
    payload = await request.json()
    schedule_id = payload.get("schedule_id")
    product_name = payload.get("product_name")

    if not product_name:
        return {"error": "product_name is required"}, 400

    # PipelineRequest 재구성
    pipeline_req = PipelineRequest(
        product_name=product_name,
        youtube_count=payload.get("youtube_count", 3),
        naver_count=payload.get("naver_count", 10),
        include_comments=payload.get("include_comments", True),
        generate_social=payload.get("generate_social", True),
        generate_video=payload.get("generate_video", True),
        generate_thumbnails=payload.get("generate_thumbnails", True),
        export_to_notion=payload.get("export_to_notion", True),
        thumbnail_count=payload.get("thumbnail_count"),
        thumbnail_styles=payload.get("thumbnail_styles"),
    )

    # Task ID 생성
    task_id = str(uuid4())

    # 파이프라인 실행
    init_pipeline_status(task_id, product_name)
    background_tasks.add_task(execute_pipeline_task, pipeline_req, task_id)

    # DB 업데이트 (last_executed_at)
    if schedule_id:
        result = await session.execute(
            select(PipelineSchedule).where(PipelineSchedule.id == schedule_id)
        )
        schedule = result.scalar_one_or_none()
        if schedule:
            schedule.last_executed_at = datetime.now()
            await session.commit()

    return {
        "status": "triggered",
        "task_id": task_id,
        "schedule_id": schedule_id,
        "product_name": product_name,
    }
