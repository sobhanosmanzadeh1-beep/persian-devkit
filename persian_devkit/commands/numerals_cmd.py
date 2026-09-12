"""دستور pdev numerals — اعداد ترتیبی فارسی."""
from __future__ import annotations

import typer
from rich.console import Console
from rich.table import Table

from persian_devkit.utils.number_utils import to_english_digits
from persian_devkit.utils.numerals_utils import to_ordinal

app = typer.Typer(help="اعداد ترتیبی و نوشتاری فارسی.", no_args_is_help=True)
console = Console()


@app.command("ordinal")
def ordinal_cmd(
    number: str = typer.Argument(..., help="عدد برای تبدیل به ترتیبی."),
) -> None:
    """تبدیل عدد به شکل ترتیبی فارسی.

    مثال: ۱ → اول، ۲ → دوم، ۲۱ → بیست و یکم
    """
    try:
        n = int(to_english_digits(number).strip())
    except ValueError:
        console.print(f"[red]✗ خطا:[/red] عدد نامعتبر: {number}")
        raise typer.Exit(1)

    try:
        console.print(to_ordinal(n))
    except ValueError as e:
        console.print(f"[red]✗ خطا:[/red] {e}")
        raise typer.Exit(1)


@app.command("table")
def table_cmd(
    start: int = typer.Argument(1, help="شروع بازه."),
    end: int = typer.Argument(20, help="پایان بازه (شامل)."),
) -> None:
    """نمایش جدول اعداد ترتیبی."""
    if start > end or end - start > 100:
        console.print("[red]✗ خطا:[/red] بازهٔ نامعتبر (حداکثر ۱۰۰ عدد).")
        raise typer.Exit(1)

    table = Table(title=" اعداد ترتیبی", title_style="bold cyan")
    table.add_column("عدد", style="bold")
    table.add_column("ترتیبی")
    for n in range(start, end + 1):
        try:
            table.add_row(str(n), to_ordinal(n))
        except ValueError:
            table.add_row(str(n), "—")
    console.print(table)