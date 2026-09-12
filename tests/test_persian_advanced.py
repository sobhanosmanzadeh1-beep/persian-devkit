"""تست‌های Batch 7 — فارسی پیشرفته."""
from __future__ import annotations

from pathlib import Path

import pytest
from typer.testing import CliRunner

from persian_devkit.main import app
from persian_devkit.utils.calendar_utils import (
    days_in_jalali_month,
    month_title,
    monthly_grid,
)
from persian_devkit.utils.hijri_utils import (
    format_hijri,
    gregorian_to_hijri,
    hijri_to_gregorian,
    hijri_to_jalali,
    jalali_to_hijri,
    parse_hijri,
)
from persian_devkit.utils.numerals_utils import to_ordinal
from persian_devkit.utils.sort_utils import sort_lines, unique_lines
from persian_devkit.utils.translit_utils import to_finglish, to_persian

runner = CliRunner()


#calendar


def test_days_in_month_basic():
    assert days_in_jalali_month(1403, 1) == 31
    assert days_in_jalali_month(1403, 7) == 30
    # اسفند: 29 یا 30
    assert days_in_jalali_month(1403, 12) in (29, 30)


def test_monthly_grid_starts_with_saturday():
    grid = monthly_grid(1403, 1)
    # 1403/01/01 چهارشنبه بود → offset = 4
    first_week = grid[0]
    assert first_week[:4] == [None, None, None, None]
    assert first_week[4] == 1


def test_monthly_grid_all_days_present():
    grid = monthly_grid(1403, 1)
    flat = [d for week in grid for d in week if d is not None]
    assert flat == list(range(1, 32))


def test_month_title():
    assert month_title(1403, 1) == "فروردین 1403"


def test_cli_calendar_show():
    r = runner.invoke(app, ["calendar", "show", "-y", "1403", "-m", "1"])
    assert r.exit_code == 0
    assert "فروردین" in r.stdout


def test_cli_calendar_today():
    r = runner.invoke(app, ["calendar", "today"])
    assert r.exit_code == 0


def test_cli_calendar_days():
    r = runner.invoke(app, ["calendar", "days", "1", "-y", "1403"])
    assert r.exit_code == 0
    assert "31" in r.stdout


#translit


def test_to_finglish_basic():
    result = to_finglish("سلام")
    # تبدیل حرف‌به‌حرف است، پس حروف اصلی باید حفظ شوند
    assert result.startswith("s")
    assert "l" in result
    assert result.endswith("m")


def test_to_finglish_full():
    result = to_finglish("سلام دنیا")
    assert "s" in result and "l" in result and "m" in result
    assert "d" in result and "n" in result


def test_to_finglish_digits():
    assert to_finglish("۱۲۳") == "123"


def test_to_finglish_zwnj():
    result = to_finglish("می‌روم")
    # نیم‌فاصله به - تبدیل می‌شود
    assert "-" in result


def test_to_persian_basic():
    result = to_persian("salam")
    assert "س" in result  # حرف اول فارسی شده


def test_cli_translit_to_finglish():
    r = runner.invoke(app, ["transliterate", "to-finglish", "سلام"])
    assert r.exit_code == 0
    assert "s" in r.stdout
    assert "m" in r.stdout


def test_cli_translit_to_persian():
    r = runner.invoke(app, ["transliterate", "to-persian", "salam"])
    assert r.exit_code == 0


#numerals


def test_to_ordinal_low():
    assert to_ordinal(1) == "اول"
    assert to_ordinal(2) == "دوم"
    assert to_ordinal(3) == "سوم"


def test_to_ordinal_teens():
    assert to_ordinal(10) == "دهم"
    assert to_ordinal(15) == "پانزدهم"


def test_to_ordinal_twenties():
    assert to_ordinal(21) == "بیست و یکم"
    assert to_ordinal(30) == "سی‌ام"


def test_to_ordinal_hundreds():
    result = to_ordinal(100)
    assert "صد" in result


def test_to_ordinal_invalid():
    with pytest.raises(ValueError):
        to_ordinal(0)
    with pytest.raises(ValueError):
        to_ordinal(-5)


def test_cli_numerals_ordinal():
    r = runner.invoke(app, ["numerals", "ordinal", "۱"])
    assert r.exit_code == 0
    assert "اول" in r.stdout


def test_cli_numerals_table():
    r = runner.invoke(app, ["numerals", "table", "1", "5"])
    assert r.exit_code == 0
    assert "اول" in r.stdout
    assert "پنجم" in r.stdout


def test_cli_numerals_invalid():
    r = runner.invoke(app, ["numerals", "ordinal", "abc"])
    assert r.exit_code == 1


#hijri


def test_gregorian_to_hijri():
    from datetime import date

    h = gregorian_to_hijri(date(2024, 3, 21))
    # حدوداً رجب یا شعبان 1445
    assert h.year == 1445


def test_hijri_to_gregorian_roundtrip():
    from datetime import date

    g = date(2024, 3, 21)
    h = gregorian_to_hijri(g)
    g2 = hijri_to_gregorian(h)
    assert g2 == g


def test_jalali_to_hijri_roundtrip():
    import jdatetime

    j = jdatetime.date(1403, 1, 2)
    h = jalali_to_hijri(j)
    j2 = hijri_to_jalali(h)
    assert j2 == j


def test_parse_hijri_slash():
    h = parse_hijri("1445/09/01")
    assert h.year == 1445


def test_parse_hijri_dash():
    h = parse_hijri("1445-09-01")
    assert h.month == 9


def test_parse_hijri_invalid():
    with pytest.raises(ValueError):
        parse_hijri("not-a-date")


def test_format_hijri():
    h = parse_hijri("1445/09/01")
    assert format_hijri(h) == "1445/09/01"


def test_cli_hijri_now():
    r = runner.invoke(app, ["hijri", "now"])
    assert r.exit_code == 0
    assert "قمری" in r.stdout


def test_cli_hijri_from_jalali():
    r = runner.invoke(app, ["hijri", "from-jalali", "1403/01/02"])
    assert r.exit_code == 0


def test_cli_hijri_from_gregorian():
    r = runner.invoke(app, ["hijri", "from-gregorian", "2024-03-21"])
    assert r.exit_code == 0


def test_cli_hijri_to_jalali():
    r = runner.invoke(app, ["hijri", "to-jalali", "1445/09/01"])
    assert r.exit_code == 0


#sort


def test_sort_lines_persian():
    lines = ["پ", "ا", "ب", "ت"]
    result = sort_lines(lines)
    # ترتیب الفبا: ا، ب، پ، ت
    assert result == ["ا", "ب", "پ", "ت"]


def test_sort_lines_reverse():
    lines = ["ا", "ب", "پ"]
    result = sort_lines(lines, reverse=True)
    assert result == ["پ", "ب", "ا"]


def test_unique_lines():
    assert unique_lines(["a", "b", "a", "c", "b"]) == ["a", "b", "c"]


def test_unique_lines_case_insensitive():
    assert unique_lines(["Foo", "foo", "BAR"]) == ["Foo", "BAR"]


def test_unique_lines_case_sensitive():
    assert unique_lines(["Foo", "foo"], case_sensitive=True) == ["Foo", "foo"]


def test_cli_sort_lines(tmp_path: Path):
    p = tmp_path / "f.txt"
    p.write_text("پ\nا\nب\nت\n", encoding="utf-8")
    r = runner.invoke(app, ["sort", "lines", "-f", str(p)])
    assert r.exit_code == 0
    out_lines = [ln.strip() for ln in r.stdout.strip().splitlines() if ln.strip()]
    assert out_lines == ["ا", "ب", "پ", "ت"]


def test_cli_sort_unique(tmp_path: Path):
    p = tmp_path / "f.txt"
    p.write_text("a\nb\na\n", encoding="utf-8")
    r = runner.invoke(app, ["sort", "unique", "-f", str(p)])
    assert r.exit_code == 0


def test_cli_sort_missing_file():
    r = runner.invoke(app, ["sort", "lines", "-f", "no-file.txt"])
    assert r.exit_code == 1