"""دستور pdev calendar — تقویم ماهانهٔ شمسی."""
from __future__ import annotations

from datetime import datetime
from typing import Optional

import jdatetime
import typer
from rich.console import Console
from rich.table import Table
from rich.text import Text

from persian_devkit.utils.calendar_utils import (
    MONTH_NAMES_FA,
    WEEKDAYS_FA_SHORT,
    days_in_jalali_month,
    month_title,
    monthly_grid,
    today_jalali,
)

app = typer.Typer(help="تقویم ماهانهٔ شمسی.", no_args_is_help=True)
console = Console()


@app.command("show")
def show_cmd(
    year: Optional[int] = typer.Option(None, "--year", "-y", help="سال شمسی."),
    month: Optional[int] = typer.Option(
        None, "--month", "-m", min=1, max=12, help="ماه (۱ تا ۱۲)."
    ),
    highlight_today: bool = typer.Option(
        True, "--today/--no-today", help="برجسته‌سازی امروز."
    ),
) -> None:
    """نمایش تقویم یک ماه شمسی."""
    today = today_jalali()
    if year is None:
        year = today.year
    if month is None:
        month = today.month

    grid = monthly_grid(year, month)
    title = month_title(year, month)

    table = Table(
        title=f" {title}",
        title_style="bold cyan",
        show_header=True,
        header_style="bold magenta",
        show_lines=False,
        padding=(0, 1),
    )
    for day in WEEKDAYS_FA_SHORT:
        table.add_column(day, justify="center", width=3)

    for week in grid:
        row: list[Text | str] = []
        for day in week:
            if day is None:
                row.append("")
                continue
            text = str(day)
            if (
                highlight_today
                and year == today.year
                and month == today.month
                and day == today.day
            ):
                row.append(Text(text, style="bold white on blue"))
            elif jdatetime.date(year, month, day).weekday() == 6:  # جمعه
                row.append(Text(text, style="red"))
            else:
                row.append(text)
        table.add_row(*row)

    console.print(table)


@app.command("today")
def today_cmd() -> None:
    """نمایش تقویم ماه جاری با برجسته‌سازی امروز."""
    today = today_jalali()
    show_cmd(year=today.year, month=today.month, highlight_today=True)


@app.command("days")
def days_cmd(
    month: int = typer.Argument(..., min=1, max=12, help="شمارهٔ ماه (۱ تا ۱۲)."),
    year: Optional[int] = typer.Option(None, "--year", "-y"),
) -> None:
    """نمایش تعداد روزهای یک ماه شمسی."""
    if year is None:
        year = today_jalali().year
    days = days_in_jalali_month(year, month)
    console.print(f"{MONTH_NAMES_FA[month - 1]} {year}: [bold]{days}[/bold] روز")