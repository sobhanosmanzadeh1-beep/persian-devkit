"""توابع کمکی تبدیل و محاسبهٔ تاریخ."""
from __future__ import annotations

from datetime import date, datetime

import jdatetime


class DateParseError(ValueError):
    """خطا در تجزیهٔ تاریخ."""


def parse_gregorian(value: str) -> date:
    """تاریخ میلادی را از رشتهٔ YYYY-MM-DD می‌خواند."""
    try:
        return datetime.strptime(value.strip(), "%Y-%m-%d").date()
    except (ValueError, AttributeError) as exc:
        raise DateParseError(f"تاریخ میلادی نامعتبر: {value}") from exc


def parse_jalali(value: str) -> jdatetime.date:
    """تاریخ شمسی را از رشتهٔ YYYY/MM/DD یا YYYY-MM-DD می‌خواند."""
    if not isinstance(value, str):
        raise DateParseError(f"تاریخ شمسی نامعتبر: {value}")
    normalized = value.strip().replace("-", "/")
    parts = normalized.split("/")
    if len(parts) != 3:
        raise DateParseError(f"تاریخ شمسی نامعتبر: {value}")
    try:
        y, m, d = (int(p) for p in parts)
        return jdatetime.date(y, m, d)
    except (ValueError, TypeError) as exc:
        raise DateParseError(f"تاریخ شمسی نامعتبر: {value}") from exc


def gregorian_to_jalali(g: date) -> jdatetime.date:
    """تبدیل تاریخ میلادی به شمسی."""
    return jdatetime.date.fromgregorian(date=g)


def jalali_to_gregorian(j: jdatetime.date) -> date:
    """تبدیل تاریخ شمسی به میلادی."""
    return j.togregorian()


def format_jalali(j: jdatetime.date) -> str:
    """قالب‌بندی تاریخ شمسی به صورت YYYY/MM/DD."""
    return f"{j.year:04d}/{j.month:02d}/{j.day:02d}"


def format_gregorian(g: date) -> str:
    """قالب‌بندی تاریخ میلادی به صورت YYYY-MM-DD."""
    return g.strftime("%Y-%m-%d")


def diff_days(a: date, b: date) -> int:
    """اختلاف روز بین دو تاریخ (b - a)."""
    return (b - a).days