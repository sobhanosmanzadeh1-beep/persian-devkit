"""دستور pdev license — تولید فایل لایسنس."""
from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.table import Table

from persian_devkit.utils.license_data import LICENSES, list_licenses, render_license

app = typer.Typer(help="تولید فایل لایسنس.", no_args_is_help=True)
console = Console()


@app.command("list")
def list_cmd() -> None:
    """نمایش لایسنس‌های موجود."""
    table = Table(title="📜 لایسنس‌ها", title_style="bold cyan")
    table.add_column("SPDX", style="bold")
    table.add_column("نام")
    for item in list_licenses():
        table.add_row(item["spdx"], item["name"])
    console.print(table)


@app.command("show")
def show_cmd(
    spdx: str = typer.Argument(..., help="نام SPDX (مثل MIT، Apache-2.0)."),
    author: str = typer.Option("Your Name", "--author", "-a", help="نام نویسنده."),
    year: Optional[int] = typer.Option(None, "--year", "-y", help="سال (پیش‌فرض: الان)."),
) -> None:
    """نمایش متن لایسنس."""
    if year is None:
        year = datetime.now().year
    try:
        console.print(render_license(spdx, author, year), highlight=False)
    except ValueError as e:
        console.print(f"[red]✗ خطا:[/red] {e}")
        raise typer.Exit(1)


@app.command("new")
def new_cmd(
    spdx: str = typer.Argument(..., help="نام SPDX."),
    author: str = typer.Option("Your Name", "--author", "-a", help="نام نویسنده."),
    year: Optional[int] = typer.Option(None, "--year", "-y"),
    output: Path = typer.Option(
        Path("LICENSE"), "--output", "-o", help="مسیر فایل خروجی."
    ),
    force: bool = typer.Option(False, "--force", "-f", help="بازنویسی فایل موجود."),
) -> None:
    """ذخیرهٔ لایسنس در فایل."""
    if year is None:
        year = datetime.now().year
    if output.exists() and not force:
        console.print(f"[red]✗ خطا:[/red] فایل موجود است: {output} (از --force استفاده کن)")
        raise typer.Exit(1)
    try:
        text = render_license(spdx, author, year)
    except ValueError as e:
        console.print(f"[red]✗ خطا:[/red] {e}")
        raise typer.Exit(1)
    output.write_text(text, encoding="utf-8")
    console.print(f"[green]✓ ذخیره شد:[/green] {output}")
