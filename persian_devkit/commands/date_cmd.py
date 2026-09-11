"""دستور pdev date — تبدیل و محاسبهٔ تاریخ شمسی و میلادی."""
from __future__ import annotations

from datetime import date, datetime

import jdatetime
import typer
from rich.console import Console
from rich.table import Table

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

app = typer.Typer(help="تبدیل و محاسبهٔ تاریخ شمسی/میلادی.", no_args_is_help=True)
console = Console()

_WEEKDAYS_FA = ["شنبه", "یکشنبه", "دوشنبه", "سه‌شنبه", "چهارشنبه", "پنجشنبه", "جمعه"]


def _fail(message: str) -> None:
    console.print(f"[red]✗ خطا:[/red] {message}")
    raise typer.Exit(1)


@app.command("to-jalali")
def to_jalali(
    value: str = typer.Argument(..., help="تاریخ میلادی به شکل YYYY-MM-DD."),
) -> None:
    """تبدیل تاریخ میلادی به شمسی."""
    try:
        g = parse_gregorian(value)
    except DateParseError as e:
        _fail(str(e))
    j = gregorian_to_jalali(g)
    console.print(f"[green]{format_jalali(j)}[/green]")


@app.command("to-gregorian")
def to_gregorian(
    value: str = typer.Argument(..., help="تاریخ شمسی به شکل YYYY/MM/DD یا YYYY-MM-DD."),
) -> None:
    """تبدیل تاریخ شمسی به میلادی."""
    try:
        j = parse_jalali(value)
    except DateParseError as e:
        _fail(str(e))
    g = jalali_to_gregorian(j)
    console.print(f"[green]{format_gregorian(g)}[/green]")


@app.command("now")
def now_cmd() -> None:
    """نمایش تاریخ و ساعت فعلی به هر دو تقویم."""
    now = datetime.now()
    j = jdatetime.datetime.fromgregorian(datetime=now)

    table = Table(title=" اکنون", show_header=False, title_style="bold cyan")
    table.add_column("تقویم", style="bold")
    table.add_column("مقدار")
    table.add_row("میلادی", now.strftime("%Y-%m-%d %H:%M:%S"))
    table.add_row("شمسی", j.strftime("%Y/%m/%d %H:%M:%S"))
    table.add_row("روز هفته", _WEEKDAYS_FA[j.weekday()])
    console.print(table)


def _auto_parse(value: str) -> date:
    """تشخیص خودکار نوع تاریخ: اگر / داشت شمسی، وگرنه میلادی."""
    if "/" in value:
        return jalali_to_gregorian(parse_jalali(value))
    return parse_gregorian(value)


@app.command("diff")
def diff_cmd(
    a: str = typer.Argument(..., help="تاریخ اول (شمسی یا میلادی)."),
    b: str = typer.Argument(..., help="تاریخ دوم (شمسی یا میلادی)."),
) -> None:
    """محاسبهٔ اختلاف بین دو تاریخ (به روز)."""
    try:
        da = _auto_parse(a)
        db = _auto_parse(b)
    except DateParseError as e:
        _fail(str(e))

    days = diff_days(da, db)
    sign = "بعد" if days >= 0 else "قبل"
    console.print(
        f"[cyan]اختلاف:[/cyan] [bold]{abs(days)}[/bold] روز "
        f"({b} {sign} از {a})"
    )