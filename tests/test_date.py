"""تست‌های مربوط به تبدیل و محاسبهٔ تاریخ."""
from datetime import date

import jdatetime
import pytest

from persian_devkit.utils.date_utils import (
    DateParseError,
    diff_days,
    format_gregorian,
    format_jalali,
    gregorian_to_jalali,
    jalali_to_gregorian,
    parse_gregorian,
    parse_jalali,
)


def test_gregorian_to_jalali():
    g = date(2024, 3, 21)
    j = gregorian_to_jalali(g)
    assert (j.year, j.month, j.day) == (1403, 1, 2)


def test_jalali_to_gregorian():
    j = jdatetime.date(1403, 1, 2)
    g = jalali_to_gregorian(j)
    assert (g.year, g.month, g.day) == (2024, 3, 21)


def test_format_jalali():
    assert format_jalali(jdatetime.date(1403, 1, 2)) == "1403/01/02"


def test_format_gregorian():
    assert format_gregorian(date(2024, 3, 21)) == "2024-03-21"


def test_parse_gregorian_valid():
    assert parse_gregorian("2024-03-21") == date(2024, 3, 21)


def test_parse_gregorian_invalid():
    with pytest.raises(DateParseError):
        parse_gregorian("2024/03/21")


def test_parse_jalali_slash():
    j = parse_jalali("1403/01/02")
    assert (j.year, j.month, j.day) == (1403, 1, 2)


def test_parse_jalali_dash():
    j = parse_jalali("1403-01-02")
    assert (j.year, j.month, j.day) == (1403, 1, 2)


def test_parse_jalali_invalid():
    with pytest.raises(DateParseError):
        parse_jalali("not-a-date")


def test_diff_days():
    assert diff_days(date(2023, 1, 1), date(2023, 1, 11)) == 10
    assert diff_days(date(2023, 1, 11), date(2023, 1, 1)) == -10