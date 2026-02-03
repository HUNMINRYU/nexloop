"""API Response 스키마"""

from datetime import datetime

from pydantic import BaseModel, ConfigDict


class ScheduleResponse(BaseModel):
    """스케줄 조회 응답"""

    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    description: str | None

    gcp_job_id: str
    cron_expression: str
    timezone: str

    product_name: str
    enabled: bool

    last_executed_at: datetime | None
    next_execution_at: datetime | None

    created_at: datetime
    updated_at: datetime
