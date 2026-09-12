"""دستور pdev uniq — حذف خطوط یا کلمات تکراری."""
from __future__ import annotations

import sys
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console

from persian_devkit.utils.sort_utils import unique_lines
from persian_devkit.utils.textstats_utils import unique_words

app = typer.Typer(help="حذف تکراری‌ها.", no_args_is_help=True)
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
    case_sensitive: bool = typer.Option(
        False, "--case-sensitive", "-c", help="حساس به بزرگی/کوچکی."
    ),
) -> None:
    """حذف خطوط تکراری با حفظ ترتیب."""
    lines = _read_lines(file)
    for ln in unique_lines(lines, case_sensitive=case_sensitive):
        console.print(ln, highlight=False, markup=False)


@app.command("words")
def words_cmd(
    text: Optional[str] = typer.Argument(None, help="متن (یا از stdin)."),
) -> None:
    """نمایش کلمات یکتای متن."""
    if text:
        content = text
    elif not sys.stdin.isatty():
        content = sys.stdin.read()
    else:
        console.print("[red]✗ خطا:[/red] متن بده یا از stdin استفاده کن.")
        raise typer.Exit(1)

    for w in unique_words(content):
        console.print(w, highlight=False, markup=False)