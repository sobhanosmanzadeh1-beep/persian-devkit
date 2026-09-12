"""دستور pdev sort — مرتب‌سازی و یکتاسازی خطوط با الفبای فارسی."""
from __future__ import annotations

import sys
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console

from persian_devkit.utils.sort_utils import sort_lines, unique_lines

app = typer.Typer(help="مرتب‌سازی خطوط با الفبای فارسی.", no_args_is_help=True)
console = Console()


def _read_lines(file: Optional[Path]) -> list[str]:
    if file is not None:
        if not file.exists():
            console.print(f"[red]✗ خطا:[/red] فایل یافت نشد: {file}")
            raise typer.Exit(1)
        return file.read_text(encoding="utf-8").splitlines()
    if not sys.stdin.isatty():
        data = sys.stdin.read()
        if data.strip():
            return data.splitlines()
    console.print("[red]✗ خطا:[/red] فایل بده یا از stdin استفاده کن.")
    raise typer.Exit(1)


@app.command("lines")
def lines_cmd(
    file: Optional[Path] = typer.Option(None, "--file", "-f", help="فایل ورودی."),
    reverse: bool = typer.Option(False, "--reverse", "-r", help="مرتب‌سازی نزولی."),
) -> None:
    """مرتب‌سازی خطوط بر اساس الفبای فارسی."""
    lines = _read_lines(file)
    for ln in sort_lines(lines, reverse=reverse):
        console.print(ln, highlight=False, markup=False)


@app.command("unique")
def unique_cmd(
    file: Optional[Path] = typer.Option(None, "--file", "-f", help="فایل ورودی."),
    case_sensitive: bool = typer.Option(
        False, "--case-sensitive", "-c", help="حساس به بزرگی/کوچکی حروف."
    ),
) -> None:
    """حذف خطوط تکراری با حفظ ترتیب."""
    lines = _read_lines(file)
    for ln in unique_lines(lines, case_sensitive=case_sensitive):
        console.print(ln, highlight=False, markup=False)


@app.command("all")
def all_cmd(
    file: Optional[Path] = typer.Option(None, "--file", "-f", help="فایل ورودی."),
) -> None:
    """ابتدا یکتاسازی، سپس مرتب‌سازی."""
    lines = _read_lines(file)
    uniq = unique_lines(lines)
    for ln in sort_lines(uniq):
        console.print(ln, highlight=False, markup=False)
