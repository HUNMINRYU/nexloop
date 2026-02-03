"""
Export Service Interface
"""

from abc import ABC, abstractmethod
from typing import Any, Dict


class ExportPort(ABC):
    """데이터 내보내기 인터페이스"""

    @abstractmethod
    def export(self, data: Dict[str, Any], output_path: str) -> str:
        """
        데이터를 특정 포맷으로 내보냅니다.

        Args:
            data: 내보낼 데이터 딕셔너리 (마케팅 분석 결과 등)
            output_path: 저장할 파일 경로 또는 식별자

        Returns:
            저장된 파일의 경로 또는 URL
        """
        pass
