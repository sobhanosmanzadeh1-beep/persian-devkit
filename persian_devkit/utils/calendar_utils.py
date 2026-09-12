"""تولید تقویم ماهانهٔ شمسی."""
from __future__ import annotations

import calendar as _pycalendar
from datetime import date, timedelta

import jdatetime

MONTH_NAMES_FA = [
    "فروردین", "اردیبهشت", "خرداد", "تیر", "مرداد", "شهریور",
    "مهر", "آبان", "آذر", "دی", "بهمن", "اسفند",
]

# شنبه = 0 تا جمعه = 6 (در jdatetime، شنبه=0)
WEEKDAYS_FA_SHORT = ["ش", "ی", "د", "س", "چ", "پ", "ج"]
WEEKDAYS_FA_LONG = [
    "شنبه", "یکشنبه", "دوشنبه", "سه‌شنبه", "چهارشنبه", "پنجشنبه", "جمعه",
]


def days_in_jalali_month(year: int, month: int) -> int:
    """تعداد روزهای یک ماه شمسی."""
    if month <= 6:
        return 31
    if month <= 11:
        return 30
    # اسفند: 29 یا 30 (سال کبیسه)
    return 30 if jdatetime.date(year, 12, 1).isleap() else 29


def today_jalali() -> jdatetime.date:
    """تاریخ امروز به شمسی."""
    return jdatetime.date.today()


def monthly_grid(year: int, month: int) -> list[list[int | None]]:
    """شبکهٔ ماهانه (لیست هفته‌ها، هر هفته ۷ روز؛ None = خانهٔ خالی).

    هفته از شنبه شروع می‌شود.
    """
    days = days_in_jalali_month(year, month)
    first = jdatetime.date(year, month, 1)
    # jdatetime.weekday(): شنبه=0 ... جمعه=6
    offset = first.weekday()

    cells: list[int | None] = [None] * offset + list(range(1, days + 1))
    # تکمیل ردیف آخر
    while len(cells) % 7 != 0:
        cells.append(None)

    return [cells[i:i + 7] for i in range(0, len(cells), 7)]


def month_title(year: int, month: int) -> str:
    """عنوان ماه: «فروردین ۱۴۰۳»."""
    return f"{MONTH_NAMES_FA[month - 1]} {year}"


def weekday_name(jdate: jdatetime.date) -> str:
    """نام روز هفته برای تاریخ شمسی."""
    return WEEKDAYS_FA_LONG[jdate.weekday()]
