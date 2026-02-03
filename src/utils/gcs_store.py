"""
GCS 업로드 헬퍼
"""

from __future__ import annotations

import re
from datetime import datetime, timezone, timedelta

# KST = UTC+9 (tzdata 없이 Windows에서도 동작)
KST = timezone(timedelta(hours=9))


def build_gcs_prefix(product: dict, kind: str) -> str:
    name = product.get("name", "product")
    safe = re.sub(r"[^0-9a-zA-Z가-힣]+", "-", str(name)).strip("-")
    safe = safe.lower()
    safe = safe[:50] if safe else "unknown"
    # 한국 시간 기준 날짜_시간 (예: 20260202_131757)
    now_kst = datetime.now(KST)
    ts = now_kst.strftime("%Y%m%d_%H%M%S")
    return f"nexloop-korea/{kind}/{safe}/{ts}"


def detect_image_ext(data: bytes) -> str:
    if data.startswith(b"\x89PNG\r\n\x1a\n"):
        return ".png"
    if data.startswith(b"\xff\xd8\xff"):
        return ".jpg"
    return ".bin"


def detect_video_ext(data: bytes) -> str:
    if b"ftyp" in data[:64]:
        return ".mp4"
    return ".bin"


def gcs_url_for(storage, path: str) -> str:
    signed = getattr(storage, "get_signed_url", lambda p: None)(path)
    if signed:
        return signed
    public = getattr(storage, "get_public_url", lambda p: None)(path)
    if public:
        return public
    bucket = getattr(storage, "bucket_name", "bucket")
    return f"gs://{bucket}/{path}"
