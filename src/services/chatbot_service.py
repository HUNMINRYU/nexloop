"""
챗봇 서비스
"""
from __future__ import annotations

import json
import re
from threading import Lock
from typing import Any
from uuid import uuid4

from config.products import get_product_catalog
from core.interfaces.ai_service import IMarketingAIService
from core.interfaces.chatbot import IRAGClient
from core.models.chatbot import ChatSession
from core.prompts import prompt_registry
from core.prompts import chatbot_prompts  # noqa: F401
from utils.logger import get_logger, log_llm_fail, log_llm_request, log_llm_response

logger = get_logger(__name__)


class ChatbotService:
    """챗봇 비즈니스 로직"""

    def __init__(self, gemini_client: IMarketingAIService, rag_client: IRAGClient) -> None:
        self._gemini_client = gemini_client
        self._rag_client = rag_client
        self._sessions: dict[str, ChatSession] = {}
        self._lock = Lock()

    def generate_reply(
        self,
        message: str,
        session_id: str | None = None,
        data_store_id: str | None = None,
    ) -> dict:
        text = message.strip()
        if not text:
            return {
                "session_id": session_id or "",
                "message": "메시지를 입력해 주세요.",
                "card": None,
                "sources": [],
            }

        session = self._get_or_create_session(session_id)
        session.add_message("user", text)

        product = self._detect_product(text)
        rag_results = self._rag_client.search(
            text,
            max_results=5,
            data_store_id=data_store_id,
        )
        use_grounding = not rag_results

        prompt = self._build_prompt(
            message=text,
            session=session,
            product=product,
            rag_results=rag_results,
        )
        log_llm_request("챗봇 응답", f"메시지 {len(text)}자, grounding={use_grounding}")

        try:
            raw_response = self._gemini_client.generate_text(
                prompt=prompt,
                temperature=0.4,
                use_grounding=use_grounding,
            )
            log_llm_response("챗봇 응답", f"응답 {len(raw_response or '')}자")
        except Exception as e:
            log_llm_fail("챗봇 응답", str(e))
            logger.error(f"챗봇 응답 생성 실패: {e}")
            raw_response = "죄송합니다. 현재 응답을 생성할 수 없습니다."

        parsed = self._parse_json_output(raw_response)
        answer = parsed.get("answer")
        if not isinstance(answer, str) or not answer.strip():
            answer = raw_response.strip()

        card = parsed.get("card") if isinstance(parsed, dict) else None
        if not isinstance(card, dict):
            card = None
        else:
            card = self._sanitize_card(card)

        session.add_message("ai", answer)

        return {
            "session_id": session.session_id,
            "message": answer,
            "card": card,
            "sources": rag_results,
        }

    def _get_or_create_session(self, session_id: str | None) -> ChatSession:
        with self._lock:
            if session_id and session_id in self._sessions:
                return self._sessions[session_id]
            new_id = session_id or str(uuid4())
            session = ChatSession(session_id=new_id)
            self._sessions[new_id] = session
            return session

    def _detect_product(self, message: str) -> dict[str, Any] | None:
        for product in get_product_catalog():
            if product.name in message:
                return product.model_dump()
        return None

    def _build_prompt(
        self,
        message: str,
        session: ChatSession,
        product: dict[str, Any] | None,
        rag_results: list[dict[str, Any]],
    ) -> str:
        recent_messages = session.messages[-6:]
        history_lines = "\n".join(
            f"- {msg.role}: {msg.content}" for msg in recent_messages
        )
        product_names = [p.name for p in get_product_catalog()]

        rag_lines = []
        for idx, item in enumerate(rag_results, start=1):
            rag_lines.append(
                f"{idx}) 제목: {item.get('title', '')}\n"
                f"   링크: {item.get('url', '')}\n"
                f"   요약: {item.get('snippet', '')}"
            )

        rag_block = "\n".join(rag_lines) if rag_lines else "검색 결과 없음"
        product_block = json.dumps(product, ensure_ascii=False, indent=2) if product else "없음"

        return prompt_registry.get("chatbot.reply").render(
            message=message,
            history_lines=history_lines,
            product_names_json=json.dumps(product_names, ensure_ascii=False),
            product_block=product_block,
            rag_block=rag_block,
        )

    def _parse_json_output(self, text: str) -> dict[str, Any]:
        cleaned = re.sub(r"```json\s*", "", text)
        cleaned = re.sub(r"```\s*$", "", cleaned)
        cleaned = cleaned.strip()

        try:
            return json.loads(cleaned)
        except json.JSONDecodeError:
            match = re.search(r"\{[\s\S]*\}", cleaned)
            if match:
                try:
                    return json.loads(match.group())
                except json.JSONDecodeError:
                    return {}
        return {}

    def _sanitize_card(self, card: dict[str, Any]) -> dict[str, Any] | None:
        title = card.get("title")
        bullets = card.get("bullets")
        cta = card.get("cta")

        if not isinstance(title, str) or not title.strip():
            return None
        if not isinstance(bullets, list):
            return None

        cleaned_bullets = [str(b).strip() for b in bullets if str(b).strip()]
        if not cleaned_bullets:
            return None

        cleaned = {
            "title": title.strip(),
            "bullets": cleaned_bullets,
        }
        if isinstance(cta, str) and cta.strip():
            cleaned["cta"] = cta.strip()
        return cleaned
