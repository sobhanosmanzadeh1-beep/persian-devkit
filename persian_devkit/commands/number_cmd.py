"""دستور `pdev number` — تبدیل و قالب‌بندی اعداد."""
from __future__ import annotations

import typer
from rich.console import Console

from persian_devkit.utils.number_utils import (
    format_thousands,
    number_to_words,
    to_english_digits,
    to_persian_digits,
)

app = typer.Typer(help="تبدیل و قالب‌بندی اعداد.", no_args_is_help=True)
console = Console()


def _fail(message: str) -> None:
    console.print(f"[red]✗ خطا:[/red] {message}")
    raise typer.Exit(1)


@app.command("to-persian")
def to_persian(
    value: str = typer.Argument(..., help="عدد یا رشته با ارقام لاتین."),
) -> None:
    """تبدیل ارقام لاتین/عربی به ارقام فارسی."""
    console.print(to_persian_digits(value))


@app.command("to-english")
def to_english(
    value: str = typer.Argument(..., help="عدد یا رشته با ارقام فارسی/عربی."),
) -> None:
    """تبدیل ارقام فارسی/عربی به ارقام لاتین."""
    console.print(to_english_digits(value))


@app.command("format")
def format_cmd(
    value: str = typer.Argument(..., help="عدد برای قالب‌بندی با جداکنندهٔ هزارگان."),
) -> None:
    """قالب‌بندی عدد با جداکنندهٔ هزارگان."""
    cleaned = to_english_digits(value).replace(",", "").replace("٫", ".").strip()
    try:
        if "." in cleaned:
            n_float = float(cleaned)
            console.print(f"{n_float:,.2f}")
        else:
            n_int = int(cleaned)
            console.print(format_thousands(n_int))
    except ValueError:
        _fail(f"عدد نامعتبر: {value}")


@app.command("words")
def words_cmd(
    value: str = typer.Argument(..., help="عدد صحیح برای تبدیل به حروف فارسی."),
) -> None:
    """تبدیل عدد صحیح به معادل نوشتاری فارسی."""
    try:
        n = int(to_english_digits(value).strip())
    except ValueError:
        _fail(f"عدد نامعتبر: {value}")
    console.print(number_to_words(n))