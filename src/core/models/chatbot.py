"""
챗봇 도메인 모델
"""
from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class ChatMessage(BaseModel):
    """챗봇 메시지"""

    model_config = ConfigDict(frozen=True)

    role: Literal["user", "ai"]
    content: str
    created_at: datetime = Field(default_factory=datetime.utcnow)


class ChatSession(BaseModel):
    """챗봇 세션"""

    session_id: str
    messages: list[ChatMessage] = Field(default_factory=list)

    def add_message(self, role: Literal["user", "ai"], content: str) -> None:
        self.messages.append(ChatMessage(role=role, content=content))
