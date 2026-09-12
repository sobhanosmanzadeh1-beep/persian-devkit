"""دستور pdev count — شمارش خطوط، کلمات، کاراکترها (مثل wc)."""
from __future__ import annotations

import sys
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.table import Table

from persian_devkit.utils.textstats_utils import text_info

app = typer.Typer(help="شمارش خطوط، کلمات و کاراکترها.", no_args_is_help=True)
console = Console()


def _read(file: Optional[Path]) -> str:
    if file is not None:
        if not file.exists():
            console.print(f"[red]✗ خطا:[/red] فایل یافت نشد: {file}")
            raise typer.Exit(1)
        return file.read_text(encoding="utf-8")
    if not sys.stdin.isatty():
        data = sys.stdin.read()
        if data:
            return data
    console.print("[red]✗ خطا:[/red] فایل بده یا از stdin استفاده کن.")
    raise typer.Exit(1)


@app.command("all")
def all_cmd(
    file: Optional[Path] = typer.Option(None, "--file", "-f", help="فایل ورودی."),
) -> None:
    """نمایش همهٔ آمار متن در جدول."""
    info = text_info(_read(file))

    table = Table(title="📊 آمار متن", title_style="bold cyan", show_header=False)
    table.add_column("شاخص", style="bold")
    table.add_column("مقدار", justify="right", style="green")
    table.add_row("خطوط", f"{info['lines']:,}")
    table.add_row("کلمات", f"{info['words']:,}")
    table.add_row("کاراکترها", f"{info['chars']:,}")
    table.add_row("کاراکترهای غیرفاصله", f"{info['chars_no_space']:,}")
    table.add_row("جملات", f"{info['sentences']:,}")
    table.add_row("پاراگراف‌ها", f"{info['paragraphs']:,}")
    table.add_row("میانگین طول کلمه", f"{info['avg_word_length']}")
    table.add_row("میانگین طول جمله", f"{info['avg_sentence_length']}")
    console.print(table)


@app.command("lines")
def lines_cmd(
    file: Optional[Path] = typer.Option(None, "--file", "-f"),
) -> None:
    """فقط تعداد خطوط."""
    console.print(str(text_info(_read(file))["lines"]))


@app.command("words")
def words_cmd(
    file: Optional[Path] = typer.Option(None, "--file", "-f"),
) -> None:
    """فقط تعداد کلمات."""
    console.print(str(text_info(_read(file))["words"]))


@app.command("chars")
def chars_cmd(
    file: Optional[Path] = typer.Option(None, "--file", "-f"),
    no_space: bool = typer.Option(
        False, "--no-space", "-n", help="فقط کاراکترهای غیرفاصله."
    ),
) -> None:
    """تعداد کاراکترها."""
    info = text_info(_read(file))
    console.print(str(info["chars_no_space"] if no_space else info["chars"]))