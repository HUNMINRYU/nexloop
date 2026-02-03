"""
제네시스코리아 API Utilities & Exports
"""

import json
import logging
import re
import time
from typing import Any, Callable, Dict, List, Optional

from config.constants import HOOK_TEMPLATES, HOOK_TYPES
from core.prompts.veo_prompt_engine import VeoPromptEngine

logger = logging.getLogger(__name__)

# === 1. Resilience Utilities ===


def retry_with_backoff(
    func: Callable,
    max_retries: int = 3,
    base_delay: float = 1.0,
    max_delay: float = 10.0,
) -> Any:
    """
    지수 백오프 재시도 유틸리티 (Standalone)

    Args:
        func: 실행할 함수 (no args)
        max_retries: 최대 재시도 횟수
        base_delay: 기본 대기 시간 (초)
        max_delay: 최대 대기 시간 (초)
    """
    last_error = None

    for attempt in range(max_retries):
        try:
            return func()
        except Exception as e:
            last_error = e
            if attempt < max_retries - 1:
                delay = min(base_delay * (2**attempt), max_delay)
                logger.warning(
                    f"Action failed. Retrying {attempt + 1}/{max_retries} in {delay:.1f}s... Error: {str(e)}"
                )
                time.sleep(delay)

    if last_error is None:
        raise RuntimeError("Retry failed without a captured exception")
    raise last_error


# === 2. Validation Utilities ===


def _extract_first_json_object(text: str) -> Optional[str]:
    """첫 번째 완전한 { ... } 블록만 추출 (중첩 괄호 대응)."""
    start = text.find("{")
    if start == -1:
        return None
    depth = 0
    for i in range(start, len(text)):
        if text[i] == "{":
            depth += 1
        elif text[i] == "}":
            depth -= 1
            if depth == 0:
                return text[start : i + 1]
    return None


def _fix_common_json_issues(raw: str) -> str:
    """LLM이 자주 내는 JSON 오류 보정 (끝 쉼표 등)."""
    # trailing comma before } or ]
    raw = re.sub(r",\s*}", "}", raw)
    raw = re.sub(r",\s*]", "]", raw)
    return raw


def validate_json_output(
    text: str,
    required_fields: Optional[List[str]] = None,
) -> Dict[str, Any]:
    """
    LLM 출력 JSON 검증 및 정화 (Standalone)

    - Markdown 코드 블록 제거
    - 첫 번째 JSON 객체만 추출 (중첩 괄호 대응)
    - 끝 쉼표 등 흔한 오류 보정 후 파싱
    - 필수 필드 확인
    """
    # 1. 마크다운 코드 블록 제거
    text = re.sub(r"```json\s*", "", text)
    text = re.sub(r"```\s*", "", text)
    text = text.strip()

    result: Dict[str, Any] = {}
    json_str: Optional[str] = None

    try:
        result = json.loads(text)
    except json.JSONDecodeError:
        json_str = _extract_first_json_object(text)
        if json_str:
            fixed = _fix_common_json_issues(json_str)
            try:
                result = json.loads(fixed)
            except json.JSONDecodeError:
                return {"error": "JSON 파싱 실패", "raw_text": text[:500]}
        else:
            return {"error": "JSON을 찾을 수 없음", "raw_text": text[:500]}

    if required_fields:
        missing = [f for f in required_fields if f not in result]
        if missing:
            result["_validation_warning"] = f"누락된 필드: {missing}"

    return result


# === 3. Hook Utilities ===


def get_hook_types() -> List[str]:
    """사용 가능한 훅 타입 목록 반환"""
    return HOOK_TYPES


def generate_hook_texts(
    product_name: str,
    hook_types: Optional[List[str]] = None,
    count: int = 5,
    custom_params: Optional[Dict[str, Any]] = None,
) -> List[Dict[str, str]]:
    """
    템플릿 기반 훅 텍스트 생성 (Rule-based)

    Args:
        product_name: 제품명
        hook_types: 생성할 훅 타입 리스트 (기본값: 전체)
        count: 최대 생성 개수
        custom_params: 템플릿 포맷팅에 사용할 추가 파라미터
    """
    if hook_types is None:
        hook_types = HOOK_TYPES

    params = {
        "product": product_name,
        "count": "10만",
        "discount": "50",
        "benefit": "효과",
        **(custom_params or {}),
    }

    hooks = []
    for hook_type in hook_types:
        if hook_type in HOOK_TEMPLATES:
            for template in HOOK_TEMPLATES[hook_type]:
                try:
                    hook = template.format(**params)
                    hooks.append({"text": hook, "type": hook_type})
                except KeyError:
                    continue

    # 중복 제거 및 개수 제한
    seen = set()
    unique_hooks = []
    for h in hooks:
        if h["text"] not in seen:
            seen.add(h["text"])
            unique_hooks.append(h)
            if len(unique_hooks) >= count:
                break

    return unique_hooks


# === 4. Prompt Engine Utilities ===


def get_prompt_example(style: str = "Cinematic") -> Dict[str, str]:
    """Veo 프롬프트 예시 반환"""
    return VeoPromptEngine.get_prompt_example(style)


__all__ = [
    "retry_with_backoff",
    "validate_json_output",
    "get_hook_types",
    "generate_hook_texts",
    "get_prompt_example",
    "VeoPromptEngine",
]
