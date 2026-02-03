"""
TTL 기반 캐시 유틸리티
API 응답 캐싱으로 호출 횟수를 줄이고 응답 속도를 개선합니다.
"""

import hashlib
import json
import time
from functools import wraps
from typing import Any, Callable, Dict, Optional

from utils.logger import get_logger

logger = get_logger(__name__)


class TTLCache:
    """
    Time-To-Live 기반 메모리 캐시

    특정 시간이 지나면 자동으로 만료되는 캐시입니다.
    API 응답 등 일정 시간 동안 유효한 데이터를 저장할 때 사용합니다.
    """

    def __init__(self, default_ttl: int = 300):
        """
        Args:
            default_ttl: 기본 캐시 유효 시간 (초), 기본값 5분
        """
        self._cache: Dict[str, Dict[str, Any]] = {}
        self._default_ttl = default_ttl
        logger.info(f"TTLCache 초기화: 기본 TTL={default_ttl}초")

    def _generate_key(self, *args, **kwargs) -> str:
        """인자들을 조합하여 고유 캐시 키 생성"""
        key_data = json.dumps(
            {"args": args, "kwargs": kwargs}, sort_keys=True, default=str
        )
        return hashlib.md5(key_data.encode()).hexdigest()

    def get(self, key: str) -> Optional[Any]:
        """캐시에서 값 조회 (만료 시 None 반환)"""
        if key not in self._cache:
            return None

        entry = self._cache[key]

        # TTL 체크
        if time.time() > entry["expires_at"]:
            logger.debug(f"캐시 만료: key={key[:8]}...")
            del self._cache[key]
            return None

        logger.debug(f"캐시 히트: key={key[:8]}...")
        return entry["value"]

    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """캐시에 값 저장"""
        ttl = ttl or self._default_ttl
        self._cache[key] = {
            "value": value,
            "expires_at": time.time() + ttl,
            "created_at": time.time(),
        }
        logger.debug(f"캐시 저장: key={key[:8]}..., ttl={ttl}초")

    def invalidate(self, key: str) -> bool:
        """특정 키의 캐시 삭제"""
        if key in self._cache:
            del self._cache[key]
            logger.debug(f"캐시 삭제: key={key[:8]}...")
            return True
        return False

    def clear(self) -> int:
        """모든 캐시 삭제"""
        count = len(self._cache)
        self._cache.clear()
        logger.info(f"전체 캐시 삭제: {count}개 항목")
        return count

    def cleanup_expired(self) -> int:
        """만료된 캐시 정리"""
        now = time.time()
        expired_keys = [
            key for key, entry in self._cache.items() if now > entry["expires_at"]
        ]
        for key in expired_keys:
            del self._cache[key]

        if expired_keys:
            logger.debug(f"만료 캐시 정리: {len(expired_keys)}개")
        return len(expired_keys)

    @property
    def stats(self) -> Dict[str, Any]:
        """캐시 통계 정보"""
        now = time.time()
        active = sum(1 for e in self._cache.values() if now <= e["expires_at"])
        return {
            "total_entries": len(self._cache),
            "active_entries": active,
            "expired_entries": len(self._cache) - active,
        }


# 전역 캐시 인스턴스 (서비스 간 공유)
_api_cache = TTLCache(default_ttl=300)  # 5분 TTL


def cached(ttl: int = 300, cache_key_prefix: str = ""):
    """
    API 응답 캐싱 데코레이터

    동일한 인자로 호출 시 캐시된 결과를 반환합니다.

    Args:
        ttl: 캐시 유효 시간 (초)
        cache_key_prefix: 캐시 키 접두사 (서비스별 구분용)

    Example:
        @cached(ttl=600, cache_key_prefix="youtube")
        def search_videos(query: str, max_results: int):
            # API 호출
            ...
    """

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            # 캐시 키 생성 (접두사 + 함수명 + 인자)
            key_base = f"{cache_key_prefix}:{func.__name__}"
            cache_key = (
                key_base + ":" + _api_cache._generate_key(*args[1:], **kwargs)
            )  # self 제외

            # 캐시 조회
            cached_result = _api_cache.get(cache_key)
            if cached_result is not None:
                logger.info(f"[캐시 히트] {func.__name__} - 캐시된 결과 반환")
                return cached_result

            # 캐시 미스: 실제 함수 실행
            logger.info(f"[캐시 미스] {func.__name__} - API 호출 실행")
            result = func(*args, **kwargs)

            # 결과 캐싱 (성공적인 결과만)
            if result is not None:
                _api_cache.set(cache_key, result, ttl)

            return result

        # 캐시 무효화 메서드 추가
        wrapped: Any = wrapper
        wrapped.invalidate_cache = lambda: _api_cache.clear()

        return wrapped

    return decorator


def get_cache_stats() -> Dict[str, Any]:
    """전역 캐시 통계 반환"""
    return _api_cache.stats


def clear_all_api_cache() -> int:
    """전역 API 캐시 모두 삭제"""
    return _api_cache.clear()
