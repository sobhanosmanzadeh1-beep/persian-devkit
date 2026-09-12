"""دستور pdev frequency — پربسامدترین کلمات."""
from __future__ import annotations

import sys
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.table import Table

from persian_devkit.utils.textstats_utils import (
    PERSIAN_STOPWORDS,
    word_frequency,
    word_frequency_no_stop,
)

app = typer.Typer(help="کلمات پربسامد متن.", no_args_is_help=True)
console = Console()


def _read(file: Optional[Path], text: Optional[str]) -> str:
    if text:
        return text
    if file is not None:
        if not file.exists():
            console.print(f"[red]✗ خطا:[/red] فایل یافت نشد: {file}")
            raise typer.Exit(1)
        return file.read_text(encoding="utf-8")
    if not sys.stdin.isatty():
        data = sys.stdin.read()
        if data:
            return data
    console.print("[red]✗ خطا:[/red] متن یا فایل بده.")
    raise typer.Exit(1)


@app.command("words")
def words_cmd(
    text: Optional[str] = typer.Argument(None, help="متن (یا از stdin)."),
    file: Optional[Path] = typer.Option(None, "--file", "-f", help="فایل ورودی."),
    top: int = typer.Option(20, "--top", "-n", min=1, max=200, help="تعداد."),
    min_length: int = typer.Option(2, "--min-length", "-l", min=1, help="حداقل طول کلمه."),
    no_stop: bool = typer.Option(
        False, "--no-stop", "-s", help="حذف کلمات رایج فارسی."
    ),
) -> None:
    """پربسامدترین کلمات متن."""
    content = _read(file, text)
    if no_stop:
        freq = word_frequency_no_stop(content, top=top, min_length=min_length)
    else:
        freq = word_frequency(content, top=top, min_length=min_length)

    if not freq:
        console.print("[yellow]⚠ کلمه‌ای یافت نشد.[/yellow]")
        return

    table = Table(title=f" {len(freq)} کلمهٔ پرتکرار", title_style="bold cyan")
    table.add_column("#", style="dim", width=3)
    table.add_column("کلمه", style="bold")
    table.add_column("تعداد", justify="right", style="green")
    for i, (word, count) in enumerate(freq, 1):
        table.add_row(str(i), word, str(count))
    console.print(table)


@app.command("stopwords")
def stopwords_cmd() -> None:
    """نمایش لیست کلمات رایج فارسی."""
    words = sorted(PERSIAN_STOPWORDS)
    console.print(f"کلمات رایج ({len(words)} کلمه):")
    for w in words:
        console.print(f"  • {w}")