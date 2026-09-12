"""دستور pdev pdf — کار با فایل‌های PDF."""
from __future__ import annotations

from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.table import Table

from persian_devkit.utils.pdf_utils import (
    extract_text,
    merge_pdfs,
    pdf_info,
    split_pdf,
)

app = typer.Typer(help="کار با فایل‌های PDF.", no_args_is_help=True)
console = Console()


def _fail(msg: str) -> None:
    console.print(f"[red]✗ خطا:[/red] {msg}")
    raise typer.Exit(1)


def _human_size(n: int) -> str:
    value = float(n)
    for unit in ("B", "KB", "MB", "GB"):
        if value < 1024:
            return f"{value:.1f} {unit}"
        value /= 1024
    return f"{value:.1f} TB"


@app.command("info")
def info_cmd(
    path: Path = typer.Argument(..., help="مسیر فایل PDF."),
) -> None:
    """اطلاعات و متادیتای PDF."""
    try:
        info = pdf_info(path)
    except ValueError as e:
        _fail(str(e))

    table = Table(title=f"📄 {path.name}", title_style="bold cyan", show_header=False)
    table.add_column("شاخص", style="bold")
    table.add_column("مقدار", style="green")
    table.add_row("تعداد صفحات", str(info["pages"]))
    table.add_row("حجم", _human_size(info["size_bytes"]))
    table.add_row("رمزگذاری‌شده؟", "✓" if info["encrypted"] else "✗")
    for key, label in (
        ("title", "عنوان"),
        ("author", "نویسنده"),
        ("subject", "موضوع"),
        ("creator", "سازنده"),
        ("producer", "تولیدکننده"),
    ):
        if info[key]:
            table.add_row(label, info[key])
    console.print(table)


@app.command("pages")
def pages_cmd(
    path: Path = typer.Argument(..., help="مسیر فایل PDF."),
) -> None:
    """تعداد صفحات PDF."""
    try:
        info = pdf_info(path)
    except ValueError as e:
        _fail(str(e))
    console.print(str(info["pages"]))


@app.command("text")
def text_cmd(
    path: Path = typer.Argument(..., help="مسیر فایل PDF."),
    start: int = typer.Option(1, "--start", "-s", min=1, help="صفحهٔ شروع (از ۱)."),
    end: Optional[int] = typer.Option(None, "--end", "-e", min=1, help="صفحهٔ پایان."),
    output: Optional[Path] = typer.Option(
        None, "--output", "-o", help="ذخیره در فایل."
    ),
) -> None:
    """استخراج متن از PDF."""
    try:
        text = extract_text(path, start=start, end=end)
    except ValueError as e:
        _fail(str(e))

    if output:
        output.write_text(text, encoding="utf-8")
        console.print(f"[green]✓ ذخیره شد:[/green] {output}")
    else:
        console.print(text, highlight=False, markup=False)


@app.command("merge")
def merge_cmd(
    files: list[Path] = typer.Argument(..., help="فایل‌های PDF برای ادغام."),
    output: Path = typer.Option(..., "--output", "-o", help="فایل خروجی."),
    force: bool = typer.Option(False, "--force", "-f", help="بازنویسی فایل موجود."),
) -> None:
    """ادغام چند PDF."""
    if output.exists() and not force:
        _fail(f"فایل موجود است: {output} (از --force استفاده کن)")
    try:
        count = merge_pdfs(files, output)
    except ValueError as e:
        _fail(str(e))
    console.print(f"[green]✓[/green] {count} صفحه در {output} ذخیره شد.")


@app.command("split")
def split_cmd(
    path: Path = typer.Argument(..., help="مسیر فایل PDF."),
    output: Path = typer.Option(..., "--output", "-o", help="فایل خروجی."),
    start: int = typer.Option(1, "--start", "-s", min=1, help="صفحهٔ شروع."),
    end: Optional[int] = typer.Option(None, "--end", "-e", min=1, help="صفحهٔ پایان."),
    force: bool = typer.Option(False, "--force", "-f"),
) -> None:
    """استخراج بازه‌ای از صفحات به PDF جدید."""
    if output.exists() and not force:
        _fail(f"فایل موجود است: {output} (از --force استفاده کن)")
    try:
        count = split_pdf(path, output, start=start, end=end)
    except ValueError as e:
        _fail(str(e))
    console.print(f"[green]✓[/green] {count} صفحه در {output} ذخیره شد.")