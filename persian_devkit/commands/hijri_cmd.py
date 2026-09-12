"""دستور pdev hijri — تبدیل تاریخ شمسی، میلادی و قمری."""
from __future__ import annotations

from datetime import datetime

import jdatetime
import typer
from rich.console import Console
from rich.table import Table

from persian_devkit.utils.date_utils import (
    format_gregorian,
    format_jalali,
    parse_gregorian,
    parse_jalali,
)
from persian_devkit.utils.hijri_utils import (
    format_hijri,
    gregorian_to_hijri,
    hijri_to_gregorian,
    hijri_to_jalali,
    jalali_to_hijri,
    parse_hijri,
)

app = typer.Typer(help="تبدیل تاریخ شمسی، میلادی و قمری.", no_args_is_help=True)
console = Console()


def _fail(msg: str) -> None:
    console.print(f"[red]✗ خطا:[/red] {msg}")
    raise typer.Exit(1)


@app.command("from-jalali")
def from_jalali_cmd(
    value: str = typer.Argument(..., help="تاریخ شمسی (YYYY/MM/DD)."),
) -> None:
    """تبدیل شمسی به قمری."""
    try:
        j = parse_jalali(value)
    except ValueError as e:
        _fail(str(e))
    h = jalali_to_hijri(j)
    console.print(f"[green]{format_hijri(h)}[/green]")


@app.command("from-gregorian")
def from_gregorian_cmd(
    value: str = typer.Argument(..., help="تاریخ میلادی (YYYY-MM-DD)."),
) -> None:
    """تبدیل میلادی به قمری."""
    try:
        g = parse_gregorian(value)
    except ValueError as e:
        _fail(str(e))
    h = gregorian_to_hijri(g)
    console.print(f"[green]{format_hijri(h)}[/green]")


@app.command("to-jalali")
def to_jalali_cmd(
    value: str = typer.Argument(..., help="تاریخ قمری (YYYY/MM/DD)."),
) -> None:
    """تبدیل قمری به شمسی."""
    try:
        h = parse_hijri(value)
    except ValueError as e:
        _fail(str(e))
    j = hijri_to_jalali(h)
    console.print(f"[green]{format_jalali(j)}[/green]")


@app.command("to-gregorian")
def to_gregorian_cmd(
    value: str = typer.Argument(..., help="تاریخ قمری (YYYY/MM/DD)."),
) -> None:
    """تبدیل قمری به میلادی."""
    try:
        h = parse_hijri(value)
    except ValueError as e:
        _fail(str(e))
    g = hijri_to_gregorian(h)
    console.print(f"[green]{format_gregorian(g)}[/green]")


@app.command("now")
def now_cmd() -> None:
    """تاریخ امروز به هر سه تقویم."""
    now = datetime.now()
    g = now.date()
    j = jdatetime.date.fromgregorian(date=g)
    h = gregorian_to_hijri(g)

    table = Table(title=" امروز", title_style="bold cyan", show_header=False)
    table.add_column("تقویم", style="bold")
    table.add_column("تاریخ", style="green")
    table.add_row("میلادی", format_gregorian(g))
    table.add_row("شمسی", format_jalali(j))
    table.add_row("قمری", format_hijri(h))
    console.print(table)