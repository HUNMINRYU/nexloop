"""
Notion Export Service
"""

from typing import Any, Dict, cast

import requests

from core.ports.export_port import ExportPort
from utils.logger import get_logger

logger = get_logger(__name__)


class NotionService(ExportPort):
    """Notion 내보내기 서비스"""

    NOTION_API_URL = "https://api.notion.com/v1"

    def __init__(self, api_key: str, database_id: str = None):
        self._api_key = api_key
        self._database_id = database_id
        self._headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "Notion-Version": "2022-06-28",
        }

    def is_configured(self) -> bool:
        """설정 확인"""
        return bool(self._api_key)

    def export(self, data: Dict[str, Any], output_path: str = None) -> str:
        """분석 결과를 Notion 페이지로 생성"""
        if not self.is_configured():
            raise ValueError("Notion API Key is not configured")

        try:
            # 1. 페이지 콘텐츠 구성
            product_name = data.get("product", {}).get("name", "제품 분석 보고서")
            analysis = data.get("analysis", {})
            children = []

            # 제목 및 개요
            children.append(self._create_header_block(f"{product_name} 마케팅 전략"))

            # 타겟 오디언스
            children.append(self._create_subheader_block("🎯 타겟 페르소나"))
            target = analysis.get("target_audience", {})
            if isinstance(target, dict):
                children.append(
                    self._create_paragraph_block(
                        f"Main Target: {target.get('primary', '-')}"
                    )
                )
                children.append(
                    self._create_paragraph_block(
                        f"Sub Target: {target.get('secondary', '-')}"
                    )
                )

                children.append(self._create_paragraph_block("Pain Points:", bold=True))
                for pt in target.get("pain_points", []):
                    children.append(self._create_bullet_block(pt))
            else:
                children.append(self._create_paragraph_block(str(target)))

            # 훅 (Hooks)
            children.append(self._create_subheader_block("🎣 바이럴 훅 (Hooks)"))
            for hook in analysis.get("hook_suggestions", []):
                children.append(self._create_number_block(hook))

            # 핵심 가치 / Differentiators
            children.append(self._create_subheader_block("💎 핵심 차별화 요소"))
            differentiators = analysis.get("competitor_analysis", {}).get(
                "differentiators", []
            )
            if not differentiators:
                differentiators = analysis.get("unique_selling_point", [])

            if isinstance(differentiators, list):
                for diff in differentiators:
                    children.append(self._create_bullet_block(diff))
            else:
                children.append(self._create_paragraph_block(str(differentiators)))

            # 인사이트
            children.append(self._create_subheader_block("💡 주요 인사이트"))
            summary = analysis.get("summary", "")
            if summary:
                children.append(self._create_quote_block(summary))

            # 2. Notion 페이지 생성
            if self._database_id:
                parent = {"database_id": self._database_id}
                db_resp = requests.get(
                    f"{self.NOTION_API_URL}/databases/{self._database_id}",
                    headers=self._headers,
                )
                if not db_resp.ok:
                    raise Exception(f"Notion DB Fetch Error: {db_resp.text}")
                db_data = db_resp.json()
                title_prop = None
                for name, prop in db_data.get("properties", {}).items():
                    if prop.get("type") == "title":
                        title_prop = name
                        break
                if not title_prop:
                    raise Exception("No title property found in database")
                properties = cast(Dict[str, Any], {
                    title_prop: {
                        "title": [{"text": {"content": f"{product_name} 리포트"}}]
                    }
                })
            elif output_path:
                parent = {"page_id": output_path}
                properties = {
                    "title": [{"text": {"content": f"{product_name} 리포트"}}]
                }
            else:
                # DB 또는 Page ID 미설정
                raise ValueError("Database ID or Page ID is required")

            response = requests.post(
                f"{self.NOTION_API_URL}/pages",
                headers=self._headers,
                json={
                    "parent": parent,
                    "properties": properties,
                    "children": children,
                },
            )
            if not response.ok:
                raise Exception(f"Notion API Error: {response.text}")

            result = response.json()
            page_url = result.get("url", "")
            logger.info(f"Notion 페이지 생성 완료: {page_url}")
            return page_url

        except Exception as e:
            logger.error(f"Notion 내보내기 실패: {e}")
            raise e

    # --- Block Builders ---
    def _create_header_block(self, text):
        return {
            "object": "block",
            "type": "heading_1",
            "heading_1": {"rich_text": [{"type": "text", "text": {"content": text}}]},
        }

    def _create_subheader_block(self, text):
        return {
            "object": "block",
            "type": "heading_2",
            "heading_2": {"rich_text": [{"type": "text", "text": {"content": text}}]},
        }

    def _create_paragraph_block(self, text, bold=False):
        return {
            "object": "block",
            "type": "paragraph",
            "paragraph": {
                "rich_text": [
                    {
                        "type": "text",
                        "text": {"content": text},
                        "annotations": {"bold": bold},
                    }
                ]
            },
        }

    def _create_bullet_block(self, text):
        return {
            "object": "block",
            "type": "bulleted_list_item",
            "bulleted_list_item": {
                "rich_text": [{"type": "text", "text": {"content": text}}]
            },
        }

    def _create_number_block(self, text):
        return {
            "object": "block",
            "type": "numbered_list_item",
            "numbered_list_item": {
                "rich_text": [{"type": "text", "text": {"content": text}}]
            },
        }

    def _create_quote_block(self, text):
        return {
            "object": "block",
            "type": "quote",
            "quote": {"rich_text": [{"type": "text", "text": {"content": text}}]},
        }
