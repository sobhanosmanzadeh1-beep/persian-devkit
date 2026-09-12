"""تبدیل تاریخ شمسی، میلادی و قمری."""
from __future__ import annotations

from datetime import date

import jdatetime
from hijridate import Gregorian as HGregorian
from hijridate import Hijri


def gregorian_to_hijri(g: date) -> Hijri:
    """تبدیل تاریخ میلادی به قمری."""
    return HGregorian(g.year, g.month, g.day).to_hijri()


def hijri_to_gregorian(h: Hijri) -> date:
    """تبدیل تاریخ قمری به میلادی."""
    g = h.to_gregorian()
    return date(g.year, g.month, g.day)


def jalali_to_hijri(j: jdatetime.date) -> Hijri:
    """تبدیل تاریخ شمسی به قمری."""
    g = j.togregorian()
    return gregorian_to_hijri(g)


def hijri_to_jalali(h: Hijri) -> jdatetime.date:
    """تبدیل تاریخ قمری به شمسی."""
    g = hijri_to_gregorian(h)
    return jdatetime.date.fromgregorian(date=g)


def parse_hijri(value: str) -> Hijri:
    """تجزیهٔ رشتهٔ تاریخ قمری به شکل YYYY/MM/DD یا YYYY-MM-DD."""
    if not isinstance(value, str):
        raise ValueError(f"تاریخ قمری نامعتبر: {value}")
    normalized = value.strip().replace("-", "/")
    parts = normalized.split("/")
    if len(parts) != 3:
        raise ValueError(f"تاریخ قمری نامعتبر: {value}")
    try:
        y, m, d = (int(p) for p in parts)
        return Hijri(y, m, d)
    except (ValueError, TypeError) as exc:
        raise ValueError(f"تاریخ قمری نامعتبر: {value}") from exc


def format_hijri(h: Hijri) -> str:
    """قالب‌بندی تاریخ قمری."""
    return f"{h.year:04d}/{h.month:02d}/{h.day:02d}"
