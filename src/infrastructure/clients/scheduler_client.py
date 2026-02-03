"""Google Cloud Scheduler API 클라이언트"""

import json
from typing import Any

from google.cloud import scheduler_v1
from google.protobuf.duration_pb2 import Duration


class CloudSchedulerClient:
    """Cloud Scheduler API 클라이언트

    GCP Cloud Scheduler Job을 생성, 수정, 삭제, 일시정지, 재개하는 기능을 제공합니다.
    """

    def __init__(self, project_id: str, location: str):
        """
        Args:
            project_id: GCP 프로젝트 ID
            location: Cloud Scheduler 리전 (예: asia-northeast3)
        """
        self.client = scheduler_v1.CloudSchedulerClient()
        self.project_id = project_id
        self.location = location
        self.parent = f"projects/{project_id}/locations/{location}"

    def create_job(
        self,
        job_id: str,
        cron_expression: str,
        timezone: str,
        target_url: str,
        payload: dict[str, Any],
    ) -> str:
        """Cloud Scheduler Job 생성

        Args:
            job_id: Job 고유 ID
            cron_expression: 크론 표현식 (예: "0 16 * * *")
            timezone: 타임존 (예: "Asia/Seoul")
            target_url: HTTP 타겟 URL
            payload: HTTP 요청 본문 (dict)

        Returns:
            생성된 Job의 전체 이름
        """
        job = scheduler_v1.Job(
            name=f"{self.parent}/jobs/{job_id}",
            schedule=cron_expression,
            time_zone=timezone,
            http_target=scheduler_v1.HttpTarget(
                uri=target_url,
                http_method=scheduler_v1.HttpMethod.POST,
                headers={"Content-Type": "application/json"},
                body=json.dumps(payload).encode(),
            ),
            attempt_deadline=Duration(seconds=180),
        )

        response = self.client.create_job(
            request=scheduler_v1.CreateJobRequest(
                parent=self.parent,
                job=job,
            )
        )
        return response.name

    def update_job(self, job_id: str, cron_expression: str, payload: dict[str, Any]) -> None:
        """Job 수정

        Args:
            job_id: Job ID
            cron_expression: 새로운 크론 표현식
            payload: 새로운 HTTP 요청 본문
        """
        name = f"{self.parent}/jobs/{job_id}"

        # 기존 job 가져오기
        job = self.client.get_job(name=name)

        # 스케줄 업데이트
        job.schedule = cron_expression
        if job.http_target:
            job.http_target.body = json.dumps(payload).encode()

        self.client.update_job(job=job)

    def delete_job(self, job_id: str) -> None:
        """Job 삭제

        Args:
            job_id: Job ID
        """
        name = f"{self.parent}/jobs/{job_id}"
        self.client.delete_job(name=name)

    def pause_job(self, job_id: str) -> None:
        """Job 일시정지

        Args:
            job_id: Job ID
        """
        name = f"{self.parent}/jobs/{job_id}"
        self.client.pause_job(name=name)

    def resume_job(self, job_id: str) -> None:
        """Job 재개

        Args:
            job_id: Job ID
        """
        name = f"{self.parent}/jobs/{job_id}"
        self.client.resume_job(name=name)

    def get_job(self, job_id: str) -> scheduler_v1.Job:
        """Job 정보 조회

        Args:
            job_id: Job ID

        Returns:
            Job 객체
        """
        name = f"{self.parent}/jobs/{job_id}"
        return self.client.get_job(name=name)
