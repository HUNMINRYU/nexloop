"""
파일 저장 유틸리티
"""

from __future__ import annotations

import time
from datetime import datetime
from pathlib import Path
from typing import Optional


def _detect_image_ext(data: bytes) -> str:
    if data.startswith(b"\x89PNG\r\n\x1a\n"):
        return ".png"
    if data.startswith(b"\xff\xd8\xff"):
        return ".jpg"
    return ".bin"


def _detect_video_ext(data: bytes) -> str:
    # MP4는 보통 ftyp 시그니처 포함
    if b"ftyp" in data[:64]:
        return ".mp4"
    return ".bin"


def ensure_output_dir(base_dir: Optional[Path] = None) -> Path:
    if base_dir is None:
        from config.settings import get_settings

        settings = get_settings()
        root = Path.cwd()
        output_dir = settings.app.output_dir
        out_dir = Path(output_dir)
        if not out_dir.is_absolute():
            out_dir = root / out_dir
    else:
        out_dir = base_dir
    out_dir.mkdir(parents=True, exist_ok=True)
    return out_dir


def save_thumbnail_bytes(data: bytes, base_dir: Optional[Path] = None) -> str:
    out_dir = ensure_output_dir(base_dir) / "thumbnails"
    out_dir.mkdir(parents=True, exist_ok=True)
    ext = _detect_image_ext(data)
    name = datetime.now().strftime("thumb_%Y%m%d_%H%M%S") + ext
    path = out_dir / name
    path.write_bytes(data)
    return str(path)


def save_video_bytes(data: bytes, base_dir: Optional[Path] = None) -> str:
    out_dir = ensure_output_dir(base_dir) / "videos"
    out_dir.mkdir(parents=True, exist_ok=True)
    ext = _detect_video_ext(data)
    name = datetime.now().strftime("video_%Y%m%d_%H%M%S") + ext
    path = out_dir / name
    path.write_bytes(data)
    return str(path)


def save_metadata(payload: dict, base_dir: Optional[Path] = None) -> str:
    out_dir = ensure_output_dir(base_dir) / "metadata"
    out_dir.mkdir(parents=True, exist_ok=True)
    name = datetime.now().strftime("meta_%Y%m%d_%H%M%S") + ".json"
    path = out_dir / name
    import json

    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return str(path)


def safe_unlink(path: Path, retries: int = 3, delay: float = 0.1) -> bool:
    """Retry file unlink for Windows file locks."""
    for attempt in range(retries):
        try:
            path.unlink()
            return True
        except PermissionError:
            if attempt < retries - 1:
                time.sleep(delay * (attempt + 1))
            else:
                raise
    return False


def safe_rmtree(path: Path, retries: int = 3, delay: float = 0.1) -> bool:
    """Retry directory removal for Windows file locks."""
    import shutil

    for attempt in range(retries):
        try:
            shutil.rmtree(path)
            return True
        except PermissionError:
            if attempt < retries - 1:
                time.sleep(delay * (attempt + 1))
            else:
                shutil.rmtree(path, ignore_errors=True)
                return False
    return False
