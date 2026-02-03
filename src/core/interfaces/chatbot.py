"""
챗봇 및 RAG 인터페이스 정의
"""
from typing import Protocol, runtime_checkable


@runtime_checkable
class IRAGClient(Protocol):
    def search(
        self,
        query: str,
        max_results: int = 5,
        data_store_id: str | None = None,
    ) -> list[dict]:
        ...

    def upsert_documents(
        self,
        documents: list[dict],
        data_store_id: str | None = None,
    ) -> int:
        ...

    def is_configured(self) -> bool:
        ...


@runtime_checkable
class IChatbotService(Protocol):
    def generate_reply(
        self,
        message: str,
        session_id: str | None = None,
        data_store_id: str | None = None,
    ) -> dict:
        ...
