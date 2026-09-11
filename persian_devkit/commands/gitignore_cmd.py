"""دستور pdev gitignore — تولید فایل .gitignore."""
from __future__ import annotations

from pathlib import Path

import typer
from rich.console import Console

from persian_devkit.utils.gitignore_data import (
    combine_gitignores,
    list_gitignores,
)

app = typer.Typer(help="تولید فایل .gitignore.", no_args_is_help=True)
console = Console()


@app.command("list")
def list_cmd() -> None:
    """نمایش زبان‌ها و ابزارهای موجود."""
    langs = list_gitignores()
    console.print("زبان‌ها و ابزارهای پشتیبانی‌شده:")
    for lang in langs:
        console.print(f"  • {lang}")


@app.command("show")
def show_cmd(
    langs: list[str] = typer.Argument(..., help="نام یک یا چند زبان/ابزار."),
) -> None:
    """نمایش محتوای .gitignore برای زبان‌های داده‌شده."""
    try:
        console.print(combine_gitignores(langs), highlight=False)
    except ValueError as e:
        console.print(f"[red]✗ خطا:[/red] {e}")
        raise typer.Exit(1)


@app.command("new")
def new_cmd(
    langs: list[str] = typer.Argument(..., help="نام یک یا چند زبان/ابزار."),
    output: Path = typer.Option(
        Path(".gitignore"), "--output", "-o", help="مسیر فایل خروجی."
    ),
    append: bool = typer.Option(
        False, "--append", "-a", help="افزودن به فایل موجود."
    ),
) -> None:
    """ساخت فایل .gitignore با ترکیب چند زبان."""
    try:
        text = combine_gitignores(langs)
    except ValueError as e:
        console.print(f"[red]✗ خطا:[/red] {e}")
        raise typer.Exit(1)

    if output.exists() and not append:
        console.print(
            f"[yellow]⚠ فایل موجود است:[/yellow] {output} (با --append ادغام می‌شود)"
        )
        raise typer.Exit(1)

    if append and output.exists():
        with output.open("a", encoding="utf-8") as f:
            f.write("\n" + text)
    else:
        output.write_text(text, encoding="utf-8")

    console.print(f"[green]✓ ذخیره شد:[/green] {output}")