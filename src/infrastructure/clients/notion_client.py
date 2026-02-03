"""
Notion Export Client
"""

from typing import Any, Dict

from notion_client import Client as NotionSyncClient

from core.ports.export_port import ExportPort
from utils.logger import get_logger

logger = get_logger(__name__)


class NotionClient(ExportPort):
    """Notion 내보내기 클라이언트"""

    def __init__(self, api_key: str = None):
        self.api_key = api_key
        self._client = None
        if api_key:
            self._client = NotionSyncClient(auth=api_key)

    def is_configured(self) -> bool:
        return bool(self._client)

    def export(self, data: Dict[str, Any], page_id: str) -> str:
        """분석 결과를 Notion 페이지의 자식 블록으로 추가"""
        if not self._client:
            raise ValueError("Notion API Key가 설정되지 않았습니다.")

        try:
            product_name = data.get("product", {}).get("name", "제품 분석")
            analysis = data.get("analysis", {})

            # Notion Block 구조 생성
            children = [
                {
                    "object": "block",
                    "type": "heading_1",
                    "heading_1": {
                        "rich_text": [
                            {"text": {"content": f"{product_name} 마케팅 전략"}}
                        ]
                    },
                },
                {
                    "object": "block",
                    "type": "callout",
                    "callout": {
                        "rich_text": [
                            {
                                "text": {
                                    "content": "제네시스코리아 스튜디오에서 생성된 자동 분석 보고서입니다."
                                }
                            }
                        ],
                        "icon": {"emoji": "🤖"},
                    },
                },
                # 타겟 페르소나
                {
                    "object": "block",
                    "type": "heading_2",
                    "heading_2": {
                        "rich_text": [{"text": {"content": "🎯 타겟 페르소나"}}]
                    },
                },
            ]

            # 타겟 정보 추가
            target = analysis.get("target_audience", {})
            if target:
                children.append(
                    {
                        "object": "block",
                        "type": "paragraph",
                        "paragraph": {
                            "rich_text": [
                                {
                                    "text": {
                                        "content": "주요 타겟: ",
                                        "annotations": {"bold": True},
                                    }
                                },
                                {"text": {"content": target.get("primary", "-")}},
                            ]
                        },
                    }
                )

            # 훅 리스트 추가
            hooks = analysis.get("hook_suggestions", [])
            if hooks:
                children.append(
                    {
                        "object": "block",
                        "type": "heading_2",
                        "heading_2": {
                            "rich_text": [{"text": {"content": "🎣 바이럴 훅 (Hooks)"}}]
                        },
                    }
                )
                for hook in hooks:
                    children.append(
                        {
                            "object": "block",
                            "type": "to_do",
                            "to_do": {
                                "rich_text": [{"text": {"content": hook}}],
                                "checked": False,
                            },
                        }
                    )

            # X-Algorithm 핵심 인사이트 추가
            insights = data.get("metrics", {}).get("top_insights", [])
            if insights:
                children.append(
                    {
                        "object": "block",
                        "type": "heading_2",
                        "heading_2": {
                            "rich_text": [{"text": {"content": "🧠 X-Algorithm 핵심 인사이트"}}]
                        },
                    }
                )
                for insight in insights:
                    score = insight.get("score", 0)
                    content = insight.get("content", "")
                    features = insight.get("features", {})

                    children.append(
                        {
                            "object": "block",
                            "type": "callout",
                            "callout": {
                                "rich_text": [
                                    {
                                        "text": {
                                            "content": f"Score {score:.2f}: \"{content}\"\n"
                                        },
                                        "annotations": {"bold": True}
                                    },
                                    {
                                        "text": {
                                            "content": f"Keywords: {', '.join(features.get('keywords', []))}\n"
                                        }
                                    },
                                    {
                                        "text": {
                                            "content": f"Purchase Intent: {features.get('purchase_intent', 0):.1f} | Viral Potential: {features.get('reply_inducing', 0):.1f}"
                                        }
                                    }
                                ],
                                "icon": {"emoji": "🔥" if score > 0.8 else "💡"},
                                "color": "yellow_background" if score > 0.8 else "default"
                            },
                        }
                    )

            # Notion API 호출: 자식 블록 추가
            self._client.blocks.children.append(block_id=page_id, children=children)

            # 페이지 URL 반환 (추정)
            return f"https://notion.so/{page_id.replace('-', '')}"

        except Exception as e:
            logger.error(f"Notion 내보내기 실패: {e}")
            raise e
