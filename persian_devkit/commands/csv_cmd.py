"""دستور pdev csv — خواندن و تبدیل فایل‌های CSV."""
from __future__ import annotations

import re
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.table import Table

from persian_devkit.utils.data_utils import dump_json, read_csv, write_csv

app = typer.Typer(help="خواندن و تبدیل فایل‌های CSV.", no_args_is_help=True)
console = Console()


def _fail(msg: str) -> None:
    console.print(f"[red]✗ خطا:[/red] {msg}")
    raise typer.Exit(1)


def _load(path: Path, delimiter: str):
    if not path.exists():
        _fail(f"فایل یافت نشد: {path}")
    try:
        return read_csv(path, delimiter=delimiter)
    except Exception as e:
        _fail(str(e))


@app.command("show")
def show_cmd(
    path: Path = typer.Argument(..., help="مسیر فایل CSV."),
    delimiter: str = typer.Option(",", "--delimiter", "-d"),
    limit: int = typer.Option(20, "--limit", "-n", min=1, help="حداکثر ردیف."),
) -> None:
    """نمایش جدولی محتوای CSV."""
    headers, rows = _load(path, delimiter)
    if not headers:
        console.print("[yellow]⚠ فایل خالی است.[/yellow]")
        return

    table = Table(title=f" {path.name}", title_style="bold cyan")
    for h in headers:
        table.add_column(h)
    for row in rows[:limit]:
        table.add_row(*[str(row.get(h, "")) for h in headers])
    console.print(table)

    if len(rows) > limit:
        console.print(f"[dim]... و {len(rows) - limit} ردیف دیگر[/dim]")


@app.command("to-json")
def to_json_cmd(
    path: Path = typer.Argument(..., help="مسیر فایل CSV."),
    delimiter: str = typer.Option(",", "--delimiter", "-d"),
    output: Optional[Path] = typer.Option(None, "--output", "-o"),
    indent: int = typer.Option(2, "--indent", "-i", min=0, max=10),
) -> None:
    """تبدیل CSV به آرایه‌ای از اشیاء JSON."""
    _, rows = _load(path, delimiter)
    text = dump_json(rows, indent=indent)
    if output:
        output.write_text(text, encoding="utf-8")
        console.print(f"[green]✓ ذخیره شد:[/green] {output}")
    else:
        console.print(text, highlight=False)


@app.command("columns")
def columns_cmd(
    path: Path = typer.Argument(..., help="مسیر فایل CSV."),
    delimiter: str = typer.Option(",", "--delimiter", "-d"),
) -> None:
    """نمایش نام ستون‌ها و تعداد ردیف‌ها."""
    headers, rows = _load(path, delimiter)
    table = Table(title=" ستون‌ها", title_style="bold cyan")
    table.add_column("ستون", style="bold")
    table.add_column("نمونه", style="dim")
    for h in headers:
        sample = str(rows[0].get(h, "")) if rows else ""
        table.add_row(h, sample[:40])
    console.print(table)
    console.print(f"تعداد ردیف: [bold]{len(rows)}[/bold]")


@app.command("filter")
def filter_cmd(
    path: Path = typer.Argument(..., help="مسیر فایل CSV."),
    column: str = typer.Argument(..., help="نام ستون."),
    pattern: str = typer.Argument(..., help="الگوی regex برای فیلتر."),
    delimiter: str = typer.Option(",", "--delimiter", "-d"),
    ignore_case: bool = typer.Option(False, "--ignore-case", "-i"),
    output: Optional[Path] = typer.Option(None, "--output", "-o"),
) -> None:
    """فیلتر ردیف‌ها بر اساس regex روی یک ستون."""
    headers, rows = _load(path, delimiter)
    if column not in headers:
        _fail(f"ستون یافت نشد: {column}")

    flags = re.IGNORECASE if ignore_case else 0
    try:
        rx = re.compile(pattern, flags)
    except re.error as e:
        _fail(f"regex نامعتبر: {e}")

    kept = [r for r in rows if rx.search(str(r.get(column, "")))]
    console.print(f"ردیف‌های مطابق: [bold]{len(kept)}[/bold] از {len(rows)}")

    if output:
        write_csv(output, headers, kept, delimiter=delimiter)
        console.print(f"[green] ذخیره شد:[/green] {output}")
    else:
        table = Table(title=f" {column} ~ {pattern}", title_style="bold cyan")
        for h in headers:
            table.add_column(h)
        for r in kept[:50]:
            table.add_row(*[str(r.get(h, "")) for h in headers])
        console.print(table)