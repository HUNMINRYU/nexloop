"""
Logging utilities for Nexloop.
"""

import logging
import sys
from typing import Callable


class ColoredFormatter(logging.Formatter):
    """Optional ANSI color formatter (ASCII-only output)."""

    COLORS = {
        "DEBUG": "\033[36m",  # Cyan
        "INFO": "\033[32m",  # Green
        "WARNING": "\033[33m",  # Yellow
        "ERROR": "\033[31m",  # Red
        "CRITICAL": "\033[35m",  # Magenta
    }
    RESET = "\033[0m"

    def format(self, record: logging.LogRecord) -> str:
        color = self.COLORS.get(record.levelname, "")
        record.color = color
        record.reset = self.RESET
        return super().format(record)


_app_logger: logging.Logger | None = None
_log_callbacks: list[Callable[[str], None]] = []


class CallbackHandler(logging.Handler):
    """Emit formatted logs to registered callbacks (for UI/debug)."""

    def __init__(self, level=logging.NOTSET):
        super().__init__(level)
        self.formatter = ColoredFormatter(
            "[%(asctime)s] %(levelname)s - %(message)s",
            datefmt="%H:%M:%S",
        )

    def emit(self, record: logging.LogRecord) -> None:
        try:
            msg = self.format(record)
            for callback in _log_callbacks:
                try:
                    callback(msg)
                except Exception:
                    pass
        except Exception:
            self.handleError(record)


def add_log_callback(callback: Callable[[str], None]) -> None:
    if callback not in _log_callbacks:
        _log_callbacks.append(callback)


def clear_log_callbacks() -> None:
    _log_callbacks.clear()


def setup_logger(name: str = "nexloop", level: int = logging.DEBUG) -> logging.Logger:
    logger = logging.getLogger(name)
    logger.setLevel(level)

    logger.handlers.clear()

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)

    formatter = ColoredFormatter(
        "[%(asctime)s] %(levelname)s - %(message)s",
        datefmt="%H:%M:%S",
    )
    console_handler.setFormatter(formatter)

    callback_handler = CallbackHandler(logging.INFO)
    callback_handler.setFormatter(formatter)

    logger.addHandler(console_handler)
    logger.addHandler(callback_handler)
    logger.propagate = False

    return logger


def _stream_is_closed(stream: object) -> bool:
    if stream is None:
        return True
    try:
        if getattr(stream, "closed", False):
            return True
    except Exception:
        return True
    try:
        writable = getattr(stream, "writable", None)
        if callable(writable) and not writable():
            return True
    except Exception:
        return True
    return False


def _has_closed_stream_handler(logger: logging.Logger) -> bool:
    for handler in logger.handlers:
        if isinstance(handler, logging.StreamHandler):
            if _stream_is_closed(getattr(handler, "stream", None)):
                return True
    return False


def get_logger(name: str = "nexloop") -> logging.Logger:
    global _app_logger
    if _app_logger is None:
        _app_logger = setup_logger(name)
        return _app_logger
    if not _app_logger.handlers or _has_closed_stream_handler(_app_logger):
        _app_logger = setup_logger(name)
    return _app_logger


def log_section(title: str) -> None:
    get_logger().info("\n" + "=" * 50)
    get_logger().info(f"== {title} ==")
    get_logger().info("=" * 50)


def log_app_start() -> None:
    log_section("App start")


def log_app_ready() -> None:
    log_success("App ready")


def log_step(step_name: str, status: str = "start", details: str = "") -> None:
    msg = f"[STEP] {step_name} - {status}"
    if details:
        msg += f" ({details})"
    get_logger().info(msg)


def log_info(message: str) -> None:
    get_logger().info(message)


def log_debug(message: str) -> None:
    get_logger().debug(message)


def log_warning(message: str) -> None:
    get_logger().warning(message)


def log_error(message: str) -> None:
    get_logger().error(message)


def log_success(message: str) -> None:
    get_logger().info(f"SUCCESS: {message}")


def log_llm_request(usage: str, details: str = "") -> None:
    msg = f"[STEP] LLM {usage} - request"
    if details:
        msg += f" ({details})"
    get_logger().info(msg)


def log_llm_response(usage: str, details: str = "") -> None:
    msg = f"LLM {usage} - response"
    if details:
        msg += f" ({details})"
    get_logger().info(msg)


def log_llm_fail(usage: str, error: str = "") -> None:
    msg = f"LLM {usage} - fail"
    if error:
        msg += f" ({error})"
    get_logger().error(msg)


def log_api_call(api_name: str, endpoint: str = "", status: str = "sent") -> None:
    get_logger().info(f"[API] {api_name} {endpoint} - {status}")


def log_api_start(api_name: str, details: str = "") -> None:
    get_logger().info(f"[API] {api_name} request start {details}")


def log_api_end(api_name: str, duration: float = 0, items: int = 0) -> None:
    msg = f"[API] {api_name} response end ({duration:.2f}s)"
    if items > 0:
        msg += f" - {items} items"
    get_logger().info(msg)


def log_process(task: str, current: int, total: int) -> None:
    percent = int((current / total) * 100) if total else 0
    bar = "#" * (percent // 10) + "-" * (10 - (percent // 10))
    get_logger().info(f"[PROCESS] {task}: [{bar}] {percent}%")


def log_timing(operation: str, duration_ms: float) -> None:
    get_logger().info(f"[TIMING] {operation}: {duration_ms:.2f}ms")


def log_tab_load(tab_name: str) -> None:
    get_logger().info(f"[TAB] {tab_name} loaded")


def log_user_action(action: str, details: str = "") -> None:
    get_logger().info(f"[USER] {action} {details}")


def log_data(label: str, value: object = None, source: str = "") -> None:
    if source:
        get_logger().info(f"[DATA] {source} {label}: {value}")
    else:
        get_logger().info(f"[DATA] {label}: {value}")


def log_function(name: str):
    def decorator(func):
        def wrapper(*args, **kwargs):
            log_debug(f"[FUNC] {name}")
            return func(*args, **kwargs)

        return wrapper

    return decorator
