"""دستور pdev url — کار با URL و query string."""
from __future__ import annotations

import sys
from typing import Optional

import typer
from rich.console import Console
from rich.table import Table

from persian_devkit.utils.url_utils import (
    build_query,
    decode_query,
    parse_url,
    url_decode,
    url_encode,
)

app = typer.Typer(help="کار با URL و query string.", no_args_is_help=True)
console = Console()


def _read(value: Optional[str]) -> str:
    if value is not None and value != "":
        return value
    if not sys.stdin.isatty():
        data = sys.stdin.read()
        if data.strip():
            return data.rstrip("\n")
    console.print("[red]✗ خطا:[/red] ورودی‌ای داده نشده.")
    raise typer.Exit(1)


@app.command("encode")
def encode_cmd(
    text: Optional[str] = typer.Argument(None, help="متن ورودی (یا از stdin)."),
    safe: str = typer.Option("", "--safe", help="کاراکترهای ایمن (رمزگذاری نمی‌شوند)."),
) -> None:
    """درصد-رمزگذاری متن."""
    console.print(url_encode(_read(text), safe=safe))


@app.command("decode")
def decode_cmd(
    text: Optional[str] = typer.Argument(None, help="رشتهٔ رمزگذاری‌شده (یا از stdin)."),
) -> None:
    """رمزگشایی متن درصد-رمزگذاری‌شده."""
    console.print(url_decode(_read(text)))


@app.command("parse")
def parse_cmd(
    url: str = typer.Argument(..., help="آدرس URL."),
) -> None:
    """تجزیهٔ URL به اجزای سازنده."""
    result = parse_url(url)
    table = Table(title="🔗 URL", title_style="bold cyan")
    table.add_column("بخش", style="bold")
    table.add_column("مقدار")

    for key in ("scheme", "netloc", "host", "port", "path", "fragment", "username"):
        value = result.get(key)
        if value:
            table.add_row(key, str(value))
    if result["query"]:
        for k, v in result["query"].items():
            table.add_row(f"query.{k}", v)
    console.print(table)


@app.command("build")
def build_cmd(
    params: list[str] = typer.Argument(
        ..., help="جفت‌های key=value برای ساخت query string."
    ),
) -> None:
    """ساخت query string از جفت‌های key=value."""
    data: dict[str, str] = {}
    for item in params:
        if "=" not in item:
            console.print(f"[red]✗ خطا:[/red] فرمت نامعتبر: {item} (باید key=value باشد)")
            raise typer.Exit(1)
        k, v = item.split("=", 1)
        data[k] = v
    console.print(build_query(data))


@app.command("decode-query")
def decode_query_cmd(
    query: str = typer.Argument(..., help="رشتهٔ query string."),
) -> None:
    """تجزیهٔ query string به کلید/مقدار."""
    result = decode_query(query)
    if not result:
        console.print("[yellow]⚠ query string خالی است.[/yellow]")
        return
    table = Table(title="📋 Query", title_style="bold cyan")
    table.add_column("کلید", style="bold")
    table.add_column("مقدار")
    for k, values in result.items():
        table.add_row(k, ", ".join(values))
    console.print(table)