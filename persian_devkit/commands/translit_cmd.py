"""دستور pdev transliterate — تبدیل فارسی ↔ فینگلیش."""
from __future__ import annotations

import sys
from typing import Optional

import typer
from rich.console import Console

from persian_devkit.utils.translit_utils import to_finglish, to_persian

app = typer.Typer(help="تبدیل فارسی ↔ فینگلیش.", no_args_is_help=True)
console = Console()


def _read(text: Optional[str]) -> str:
    if text is not None and text != "":
        return text
    if not sys.stdin.isatty():
        data = sys.stdin.read()
        if data.strip():
            return data.rstrip("\n")
    console.print("[red]✗ خطا:[/red] متنی وارد نشده.")
    raise typer.Exit(1)


@app.command("to-finglish")
def to_finglish_cmd(
    text: Optional[str] = typer.Argument(None, help="متن فارسی (یا از stdin)."),
) -> None:
    """تبدیل متن فارسی به فینگلیش.

    مثال: «سلام دنیا» → «salam donya»
    """
    console.print(to_finglish(_read(text)))


@app.command("to-persian")
def to_persian_cmd(
    text: Optional[str] = typer.Argument(None, help="متن فینگلیش (یا از stdin)."),
) -> None:
    """تبدیل متن فینگلیش به فارسی (تقریبی).

    مثال: «salam» → «سالام»
    """
    console.print(to_persian(_read(text)))