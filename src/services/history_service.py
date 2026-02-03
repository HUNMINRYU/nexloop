"""
히스토리 서비스
파이프라인 실행 결과(Metadata)의 로드, 검색, 삭제 관리
"""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from core.models.pipeline import (
    PipelineResult,
)
from utils.file_store import ensure_output_dir, safe_unlink
from utils.logger import get_logger

logger = get_logger(__name__)


class HistoryService:
    """분석 히스토리 관리 서비스"""

    def __init__(self, base_dir: Optional[Path] = None):
        self._base_dir = base_dir

    def get_history_list(self) -> List[Dict[str, Any]]:
        """저장된 히스토리 목록 반환 (최신순)"""
        try:
            meta_dir = ensure_output_dir(self._base_dir) / "metadata"
            if not meta_dir.exists():
                return []

            files = sorted(meta_dir.glob("meta_*.json"), key=os.path.getmtime, reverse=True)

            history = []
            for f in files:
                try:
                    data = json.loads(f.read_text(encoding="utf-8"))
                    history.append({
                        "id": f.stem,
                        "file_path": str(f),
                        "product_name": data.get("product_name", "N/A"),
                        "executed_at": data.get("executed_at", ""),
                        "success": data.get("success", False),
                        "top_insight_count": len(data.get("collected_data", {}).get("top_insights", [])),
                        "has_video": bool(data.get("generated_content", {}).get("video_url") or data.get("generated_content", {}).get("video_path")),
                    })
                except Exception as e:
                    logger.error(f"히스토리 파일 로드 실패 ({f.name}): {e}")

            return history
        except Exception as e:
            logger.error(f"히스토리 목록 조회 실패: {e}")
            return []

    def load_history(self, history_id: str) -> Optional[PipelineResult]:
        """특정 히스토리 로드 및 PipelineResult 객체로 복원"""
        try:
            meta_dir = ensure_output_dir(self._base_dir) / "metadata"
            file_path = meta_dir / f"{history_id}.json"

            if not file_path.exists():
                logger.warning(f"히스토리 파일을 찾을 수 없음: {file_path}")
                return None

            data = json.loads(file_path.read_text(encoding="utf-8"))

            # datetime 문자열 복구
            if "executed_at" in data and isinstance(data["executed_at"], str):
                try:
                    data["executed_at"] = datetime.fromisoformat(data["executed_at"])
                except ValueError:
                    data["executed_at"] = datetime.now()

            # Pydantic 모델로 변환 (bytes 데이터는 제외된 상태로 로드됨)
            try:
                return PipelineResult(**data)
            except Exception:
                # Legacy metadata fallback
                if "success" not in data:
                    status = data.get("status") or data.get("state")
                    data["success"] = status == "success"
                if "product_name" not in data:
                    product = data.get("product") or {}
                    if isinstance(product, dict):
                        data["product_name"] = product.get("name") or data.get("product_name")
                    else:
                        data["product_name"] = product or data.get("name")
                if not isinstance(data.get("product_name"), str):
                    data["product_name"] = str(data.get("product_name") or "unknown")
                return PipelineResult(**data)
        except Exception as e:
            logger.error(f"히스토리 로드 실패 ({history_id}): {e}")
            return None

    def delete_history(self, history_id: str) -> bool:
        """히스토리 삭제 (메타데이터 파일만 삭제)"""
        try:
            meta_dir = ensure_output_dir(self._base_dir) / "metadata"
            file_path = meta_dir / f"{history_id}.json"

            if file_path.exists():
                return safe_unlink(file_path)
            return False
        except Exception as e:
            logger.error(f"히스토리 삭제 실패 ({history_id}): {e}")
            return False

    def save_result(self, result: PipelineResult) -> str:
        """PipelineResult를 영구 저장 (바이트 데이터 제외)"""
        try:
            # Pydantic 모델을 dict로 변환 (bytes는 수동 제외)
            data = result.model_dump()

            # 대용량 바이트 데이터는 저장 시 제외 (이미 별도 파일로 저장됨)
            if "generated_content" in data and data["generated_content"]:
                data["generated_content"].pop("thumbnail_data", None)
                data["generated_content"].pop("video_bytes", None)

                # multi_thumbnails에서도 image 바이트 제거
                if "multi_thumbnails" in data["generated_content"]:
                    for item in data["generated_content"]["multi_thumbnails"]:
                        item.pop("image", None)
                        item.pop("image_bytes", None)

            # datetime 직렬화
            if isinstance(data.get("executed_at"), datetime):
                data["executed_at"] = data["executed_at"].isoformat()

            from utils.file_store import save_metadata
            return save_metadata(data, self._base_dir)
        except Exception as e:
            logger.error(f"결과 저장 실패: {e}")
            return ""
