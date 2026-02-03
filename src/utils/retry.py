"""재시도 데코레이터"""
from __future__ import annotations

import asyncio
import time
from typing import Callable, TypeVar

from core.exceptions import NexloopError, classify_error

F = TypeVar("F", bound=Callable[..., object])


def retry_on_error(
    max_attempts: int = 3,
    base_delay: float = 1.0,
    max_delay: float = 10.0,
):
    def decorator(func: F) -> F:
        if asyncio.iscoroutinefunction(func):
            async def async_wrapper(*args, **kwargs):
                attempt = 0
                while True:
                    try:
                        return await func(*args, **kwargs)
                    except Exception as exc:
                        nex_err = exc if isinstance(exc, NexloopError) else classify_error(exc)
                        if not nex_err.is_retryable() or attempt >= max_attempts - 1:
                            raise
                        delay = nex_err.get_retry_delay() or min(base_delay * (2 ** attempt), max_delay)
                        await asyncio.sleep(delay)
                        attempt += 1

            return async_wrapper  # type: ignore[return-value]

        def sync_wrapper(*args, **kwargs):
            attempt = 0
            while True:
                try:
                    return func(*args, **kwargs)
                except Exception as exc:
                    nex_err = exc if isinstance(exc, NexloopError) else classify_error(exc)
                    if not nex_err.is_retryable() or attempt >= max_attempts - 1:
                        raise
                    delay = nex_err.get_retry_delay() or min(base_delay * (2 ** attempt), max_delay)
                    time.sleep(delay)
                    attempt += 1

        return sync_wrapper  # type: ignore[return-value]

    return decorator
