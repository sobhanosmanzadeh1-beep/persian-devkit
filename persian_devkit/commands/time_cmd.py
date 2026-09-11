"""دستور pdev time — کار با timestamp و مدت زمان."""
from __future__ import annotations

from datetime import datetime, timezone

import typer
from rich.console import Console
from rich.table import Table

from persian_devkit.utils.time_utils import (
    from_unix,
    humanize_duration,
    now_unix,
    parse_duration,
    to_unix,
)

app = typer.Typer(help="کار با timestamp و مدت زمان.", no_args_is_help=True)
console = Console()


@app.command("now")
def now_cmd(
    ms: bool = typer.Option(False, "--ms", help="خروجی به میلی‌ثانیه."),
) -> None:
    """نمایش timestamp فعلی."""
    ts = now_unix()
    console.print(ts * 1000 if ms else ts)


@app.command("to-unix")
def to_unix_cmd(
    value: str = typer.Argument(
        ..., help="تاریخ به شکل YYYY-MM-DD یا YYYY-MM-DD HH:MM:SS."
    ),
) -> None:
    """تبدیل تاریخ میلادی به timestamp."""
    for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d"):
        try:
            dt = datetime.strptime(value.strip(), fmt)
            console.print(to_unix(dt))
            return
        except ValueError:
            continue
    console.print(f"[red]✗ خطا:[/red] فرمت تاریخ نامعتبر: {value}")
    raise typer.Exit(1)


@app.command("from-unix")
def from_unix_cmd(
    ts: int = typer.Argument(..., help="timestamp (ثانیه)."),
    local: bool = typer.Option(False, "--local", help="نمایش در زمان محلی."),
) -> None:
    """تبدیل timestamp به تاریخ میلادی."""
    dt = from_unix(ts)
    if local:
        dt = dt.astimezone()
        console.print(dt.strftime("%Y-%m-%d %H:%M:%S %Z"))
    else:
        console.print(dt.strftime("%Y-%m-%d %H:%M:%S UTC"))


@app.command("duration")
def duration_cmd(
    value: str = typer.Argument(
        ..., help="مدت زمان (مثل '2h30m' یا '2 ساعت و 30 دقیقه')."
    ),
) -> None:
    """تبدیل رشتهٔ مدت زمان به ثانیه و معادل خوانا."""
    try:
        seconds = parse_duration(value)
    except ValueError as e:
        console.print(f"[red]✗ خطا:[/red] {e}")
        raise typer.Exit(1)

    table = Table(title="⏱  مدت زمان", title_style="bold cyan", show_header=False)
    table.add_column("شاخص", style="bold")
    table.add_column("مقدار", style="green")
    table.add_row("ثانیه", f"{seconds:,}")
    table.add_row("خوانا", humanize_duration(seconds))
    console.print(table)


@app.command("ago")
def ago_cmd(
    ts: int = typer.Argument(..., help="timestamp در گذشته."),
) -> None:
    """نمایش فاصلهٔ زمانی از یک timestamp تا الان."""
    now = now_unix()
    delta = now - ts
    if delta < 0:
        console.print(
            f"[yellow]⚠ این زمان در آینده است:[/yellow] {humanize_duration(-delta)} بعد"
        )
    else:
        console.print(f"{humanize_duration(delta)} پیش")