"""파이프라인 스케줄러 서비스"""

import os
from datetime import datetime
from uuid import uuid4

from sqlalchemy.orm import Session

from src.infrastructure.clients.scheduler_client import CloudSchedulerClient
from src.infrastructure.database.models import PipelineSchedule
from src.schemas.requests import ScheduleRequest


class SchedulerService:
    """파이프라인 스케줄 관리 서비스

    Cloud Scheduler Job과 DB를 동기화하여 파이프라인 스케줄을 관리합니다.
    """

    def __init__(self, db: Session, scheduler_client: CloudSchedulerClient):
        self.db = db
        self.scheduler = scheduler_client

    def create_schedule(self, req: ScheduleRequest, user_id: int) -> PipelineSchedule:
        """스케줄 생성

        Args:
            req: 스케줄 생성 요청
            user_id: 생성자 ID

        Returns:
            생성된 스케줄 객체
        """
        # 크론 표현식 생성
        cron = self._build_cron(req.days_of_week, req.hour, req.minute, req.frequency)

        # GCP Job ID 생성 (제품명 + 랜덤 8자리)
        gcp_job_id = f"pipeline-{req.product_name.replace(' ', '-')}-{uuid4().hex[:8]}"

        # Webhook URL
        webhook_url = f"{os.getenv('APP_URL')}/api/v1/webhooks/scheduler"

        # Payload (schedule_id는 나중에 업데이트)
        payload = {
            "schedule_id": None,
            "product_name": req.product_name,
            **req.pipeline_config.model_dump()
        }

        # Cloud Scheduler Job 생성
        try:
            self.scheduler.create_job(
                job_id=gcp_job_id,
                cron_expression=cron,
                timezone=req.timezone,
                target_url=webhook_url,
                payload=payload,
            )
        except Exception as e:
            raise ValueError(f"Cloud Scheduler Job 생성 실패: {str(e)}") from e

        # DB 저장
        schedule = PipelineSchedule(
            name=req.name,
            description=req.description,
            gcp_job_id=gcp_job_id,
            cron_expression=cron,
            timezone=req.timezone,
            product_name=req.product_name,
            config_json=req.pipeline_config.model_dump_json(),
            enabled=True,
            created_by=user_id,
        )
        self.db.add(schedule)
        self.db.commit()
        self.db.refresh(schedule)

        # Payload에 schedule_id 추가하고 Job 업데이트
        payload["schedule_id"] = schedule.id
        try:
            self.scheduler.update_job(gcp_job_id, cron, payload)
        except Exception:
            # Job 업데이트 실패 시 무시 (schedule_id는 선택적)
            pass

        return schedule

    def update_schedule(self, schedule_id: int, req: ScheduleRequest) -> PipelineSchedule:
        """스케줄 수정

        Args:
            schedule_id: 스케줄 ID
            req: 스케줄 수정 요청

        Returns:
            수정된 스케줄 객체
        """
        schedule = self.db.query(PipelineSchedule).filter(
            PipelineSchedule.id == schedule_id,
            PipelineSchedule.deleted_at.is_(None)
        ).first()

        if not schedule:
            raise ValueError(f"스케줄을 찾을 수 없습니다: {schedule_id}")

        # 크론 표현식 재생성
        cron = self._build_cron(req.days_of_week, req.hour, req.minute, req.frequency)

        # Payload 업데이트
        payload = {
            "schedule_id": schedule_id,
            "product_name": req.product_name,
            **req.pipeline_config.model_dump()
        }

        # Cloud Scheduler Job 업데이트
        try:
            self.scheduler.update_job(schedule.gcp_job_id, cron, payload)
        except Exception as e:
            raise ValueError(f"Cloud Scheduler Job 업데이트 실패: {str(e)}") from e

        # DB 업데이트
        schedule.name = req.name
        schedule.description = req.description
        schedule.cron_expression = cron
        schedule.product_name = req.product_name
        schedule.config_json = req.pipeline_config.model_dump_json()
        self.db.commit()
        self.db.refresh(schedule)

        return schedule

    def delete_schedule(self, schedule_id: int) -> None:
        """스케줄 삭제 (소프트 삭제 + GCP Job 삭제)

        Args:
            schedule_id: 스케줄 ID
        """
        schedule = self.db.query(PipelineSchedule).filter(
            PipelineSchedule.id == schedule_id,
            PipelineSchedule.deleted_at.is_(None)
        ).first()

        if not schedule:
            raise ValueError(f"스케줄을 찾을 수 없습니다: {schedule_id}")

        # Cloud Scheduler Job 삭제
        try:
            self.scheduler.delete_job(schedule.gcp_job_id)
        except Exception:
            # Job 삭제 실패 시에도 DB에서는 삭제 (이미 삭제되었거나 없을 수 있음)
            pass

        # DB 소프트 삭제
        schedule.deleted_at = datetime.now()
        schedule.enabled = False
        self.db.commit()

    def toggle_schedule(self, schedule_id: int, enabled: bool) -> None:
        """스케줄 활성화/비활성화

        Args:
            schedule_id: 스케줄 ID
            enabled: 활성화 여부
        """
        schedule = self.db.query(PipelineSchedule).filter(
            PipelineSchedule.id == schedule_id,
            PipelineSchedule.deleted_at.is_(None)
        ).first()

        if not schedule:
            raise ValueError(f"스케줄을 찾을 수 없습니다: {schedule_id}")

        # Cloud Scheduler Job 활성화/비활성화
        try:
            if enabled:
                self.scheduler.resume_job(schedule.gcp_job_id)
            else:
                self.scheduler.pause_job(schedule.gcp_job_id)
        except Exception as e:
            raise ValueError(f"Cloud Scheduler Job 상태 변경 실패: {str(e)}") from e

        # DB 업데이트
        schedule.enabled = enabled
        self.db.commit()

    def _build_cron(
        self,
        days: list[int],
        hour: int,
        minute: int,
        frequency: str
    ) -> str:
        """크론 표현식 생성

        Args:
            days: 요일 리스트 (0=월, 6=일), 비어있으면 매일
            hour: 시간 (0-23)
            minute: 분 (0-59)
            frequency: 'daily' | 'weekly' | 'custom'

        Returns:
            크론 표현식 (예: "0 16 * * 1,3,5")
        """
        if frequency == 'daily':
            return f"{minute} {hour} * * *"

        if frequency == 'weekly' and days:
            # UI의 0=월을 크론의 1=월로 변환 (크론: 0=일, 1=월, ...)
            day_str = ','.join(str((d + 1) % 7) for d in days)
            return f"{minute} {hour} * * {day_str}"

        # Custom: 사용자 지정
        if days:
            day_str = ','.join(str((d + 1) % 7) for d in days)
            return f"{minute} {hour} * * {day_str}"

        return f"{minute} {hour} * * *"
