"""
Export Service Facade
"""

from typing import Any, Dict

from infrastructure.services.notion_service import NotionService
from infrastructure.services.pdf_service import PdfService


class ExportService:
    """내보내기 통합 서비스"""

    def __init__(self, settings):
        self._pdf_service = PdfService()
        self._notion_service = NotionService(
            api_key=getattr(settings, "notion_api_key", ""),
            database_id=getattr(settings, "notion_database_id", ""),
        )

    def export_pdf(self, data: Dict[str, Any], output_path: str) -> str:
        """PDF로 내보내기"""
        return self._pdf_service.export(data, output_path)

    def export_notion(self, data: Dict[str, Any], parent_page_id: str = None) -> str:
        """Notion으로 내보내기"""
        # 설정에 DB ID가 있으면 그것을 우선 사용, 아니면 인자로 받은 page_id 사용
        # NotionService 내부에서 처리
        return self._notion_service.export(data, parent_page_id)
