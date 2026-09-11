"""دستور `pdev text` — پاک‌سازی و پردازش متن فارسی."""
from __future__ import annotations

import sys
from typing import Optional

import typer
from rich.console import Console
from rich.table import Table

from persian_devkit.utils.text_utils import (
    change_case,
    diff_lines,
    fix_halfspace,
    normalize,
    regex_test,
    reverse_text,
    text_stats,
    to_slug,
)

app = typer.Typer(help="پاک‌سازی و پردازش متن فارسی.", no_args_is_help=True)
console = Console()


def _read_text(value: Optional[str]) -> str:
    """اگر مقدار داده نشد، از stdin می‌خواند."""
    if value is not None and value != "":
        return value
    try:
        if not sys.stdin.isatty():
            data = sys.stdin.read()
            if data.strip():
                return data.rstrip("\n")
    except (AttributeError, OSError):
        pass
    console.print(
        "[red]✗ خطا:[/red] متنی وارد نشده. یک آرگومان بده یا از stdin استفاده کن."
    )
    raise typer.Exit(1)


@app.command("halfspace")
def halfspace_cmd(
    text: Optional[str] = typer.Argument(
        None, help="متن ورودی (اگر ندهی، از stdin خوانده می‌شود)."
    ),
) -> None:
    """اصلاح نیم‌فاصله در متن فارسی."""
    console.print(fix_halfspace(_read_text(text)))


@app.command("normalize")
def normalize_cmd(
    text: Optional[str] = typer.Argument(
        None, help="متن ورودی (اگر ندهی، از stdin خوانده می‌شود)."
    ),
) -> None:
    """یکسان‌سازی حروف (ی/ک عربی) و حذف فاصله‌های اضافه."""
    console.print(normalize(_read_text(text)))


@app.command("reverse")
def reverse_cmd(
    text: Optional[str] = typer.Argument(
        None, help="متن ورودی (اگر ندهی، از stdin خوانده می‌شود)."
    ),
) -> None:
    """معکوس‌سازی متن."""
    console.print(reverse_text(_read_text(text)))


@app.command("stats")
def stats_cmd(
    text: Optional[str] = typer.Argument(
        None, help="متن ورودی (اگر ندهی، از stdin خوانده می‌شود)."
    ),
) -> None:
    """نمایش آمار متن (کاراکتر، کلمه، خط، جمله)."""
    stats = text_stats(_read_text(text))

    table = Table(title=" آمار متن", title_style="bold cyan")
    table.add_column("شاخص", style="bold")
    table.add_column("مقدار", justify="right", style="green")
    table.add_row("کاراکترها", str(stats["chars"]))
    table.add_row("کاراکترهای غیرفاصله", str(stats["chars_no_space"]))
    table.add_row("کلمات", str(stats["words"]))
    table.add_row("خطوط", str(stats["lines"]))
    table.add_row("جملات", str(stats["sentences"]))
    console.print(table)

@app.command("slug")
def slug_cmd(
    text: Optional[str] = typer.Argument(None, help="متن ورودی (یا از stdin)."),
    separator: str = typer.Option("-", "--sep", "-s", help="جداکننده."),
    max_length: int = typer.Option(
        0, "--max-length", "-m", min=0, help="حداکثر طول (۰ = بدون محدودیت)."
    ),
) -> None:
    """تبدیل متن به slug قابل استفاده در URL."""
    console.print(to_slug(_read_text(text), separator=separator, max_length=max_length))


@app.command("case")
def case_cmd(
    mode: str = typer.Argument(
        ..., help="حالت: upper, lower, title, capitalize, swap."
    ),
    text: Optional[str] = typer.Argument(None, help="متن ورودی (یا از stdin)."),
) -> None:
    """تغییر حالت حروف متن."""
    try:
        console.print(change_case(_read_text(text), mode))
    except ValueError as e:
        console.print(f"[red]✗ خطا:[/red] {e}")
        raise typer.Exit(1)


@app.command("diff")
def diff_cmd(
    a: str = typer.Argument(..., help="متن اول."),
    b: str = typer.Argument(..., help="متن دوم."),
) -> None:
    """مقایسهٔ خطی دو متن (مانند diff)."""
    lines = diff_lines(a, b)
    if not lines:
        console.print("[green]✓ دو متن یکسان هستند.[/green]")
        return
    for sign, line in lines:
        if sign == "-":
            console.print(f"[red]- {line}[/red]")
        elif sign == "+":
            console.print(f"[green]+ {line}[/green]")
        else:
            console.print(f"[dim]  {line}[/dim]")


@app.command("regex")
def regex_cmd(
    pattern: str = typer.Argument(..., help="الگوی regex."),
    text: Optional[str] = typer.Argument(None, help="متن ورودی (یا از stdin)."),
) -> None:
    """اجرای الگوی regex روی متن و نمایش نتایج."""
    try:
        result = regex_test(pattern, _read_text(text))
    except ValueError as e:
        console.print(f"[red]✗ خطا:[/red] {e}")
        raise typer.Exit(1)

    if result["is_match"]:
        console.print("[green]✓ مطابقت یافت شد.[/green]")
    else:
        console.print("[yellow]⚠ مطابقتی یافت نشد.[/yellow]")

    console.print(f"تعداد: [bold]{result['count']}[/bold]")
    for m in result["matches"][:20]:
        console.print(f"  • {m}")