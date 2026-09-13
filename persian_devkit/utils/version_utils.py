"""توابع کمکی اطلاعات نسخه و PyPI."""
from __future__ import annotations

from typing import Optional

import httpx

from persian_devkit import __version__

PYPI_JSON_URL = "https://pypi.org/pypi/persian-devkit/json"


def current_version() -> str:
    """نسخهٔ فعلی نصب‌شده."""
    return __version__


def latest_version(timeout: float = 5.0) -> Optional[str]:
    """آخرین نسخه در PyPI (یا None اگر اتصال نبود)."""
    try:
        r = httpx.get(PYPI_JSON_URL, timeout=timeout)
        if r.status_code == 200:
            data = r.json()
            return data.get("info", {}).get("version")
    except (httpx.HTTPError, ValueError):
        return None
    return None


def _parse_version(v: str) -> tuple[int, ...]:
    """تبدیل رشتهٔ نسخه به tuple از اعداد."""
    parts: list[int] = []
    for p in v.split("."):
        try:
            parts.append(int(p))
        except ValueError:
            # مثل "1.0.0b1"
            num = ""
            for ch in p:
                if ch.isdigit():
                    num += ch
                else:
                    break
            parts.append(int(num) if num else 0)
    return tuple(parts)


def is_newer(latest: str, current: str) -> bool:
    """آیا نسخهٔ latest از current جدیدتر است؟"""
    return _parse_version(latest) > _parse_version(current)