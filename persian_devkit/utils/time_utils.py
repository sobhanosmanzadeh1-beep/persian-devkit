"""توابع کمکی کار با زمان و timestamp."""
from __future__ import annotations

import re
from datetime import datetime, timezone

_DURATION_RE = re.compile(
    r"(?P<value>\d+)\s*(?P<unit>s|m|h|d|w|ثانیه|دقیقه|ساعت|روز|هفته)",
    re.IGNORECASE,
)

_UNIT_SECONDS = {
    "s": 1,
    "m": 60,
    "h": 3600,
    "d": 86400,
    "w": 604800,
    "ثانیه": 1,
    "دقیقه": 60,
    "ساعت": 3600,
    "روز": 86400,
    "هفته": 604800,
}


def now_unix() -> int:
    """timestamp فعلی به ثانیه."""
    return int(datetime.now(tz=timezone.utc).timestamp())


def to_unix(dt: datetime) -> int:
    """تبدیل datetime به timestamp (اگر timezone نداشته باشد، UTC فرض می‌شود)."""
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return int(dt.timestamp())


def from_unix(ts: int) -> datetime:
    """تبدیل timestamp به datetime (UTC)."""
    return datetime.fromtimestamp(ts, tz=timezone.utc)


def parse_duration(text: str) -> int:
    """تبدیل رشتهٔ مدت زمان (مثل '2h30m' یا '2 ساعت و 30 دقیقه') به ثانیه."""
    if not text or not text.strip():
        raise ValueError("رشتهٔ مدت زمان خالی است.")

    total = 0
    found = False
    for match in _DURATION_RE.finditer(text):
        value = int(match.group("value"))
        unit = match.group("unit").lower()
        if unit not in _UNIT_SECONDS:
            raise ValueError(f"واحد ناشناخته: {unit}")
        total += value * _UNIT_SECONDS[unit]
        found = True

    if not found:
        raise ValueError(f"فرمت مدت زمان نامعتبر: {text}")
    return total


def humanize_duration(seconds: int) -> str:
    """تبدیل ثانیه به رشتهٔ خوانا (فارسی)."""
    if seconds < 0:
        return "منفی " + humanize_duration(-seconds)
    if seconds == 0:
        return "۰ ثانیه"

    parts: list[str] = []
    for label, unit in (
        ("هفته", 604800),
        ("روز", 86400),
        ("ساعت", 3600),
        ("دقیقه", 60),
        ("ثانیه", 1),
    ):
        if seconds >= unit:
            value, seconds = divmod(seconds, unit)
            parts.append(f"{value} {label}")
    return " و ".join(parts)