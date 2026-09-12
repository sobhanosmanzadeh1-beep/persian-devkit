"""دستور pdev extract — استخراج الگوها از متن."""
from __future__ import annotations

import sys
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.table import Table

from persian_devkit.utils.textstats_utils import (
    extract_emails,
    extract_hashtags,
    extract_ips,
    extract_mentions,
    extract_numbers,
    extract_urls,
)

app = typer.Typer(help="استخراج الگوها از متن.", no_args_is_help=True)
console = Console()


def _read(text: Optional[str], file: Optional[Path]) -> str:
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


def _print_list(title: str, items: list[str], style: str = "green") -> None:
    if not items:
        console.print(f"[yellow]⚠ {title}: موردی یافت نشد.[/yellow]")
        return
    console.print(f"[bold]{title}[/bold] ({len(items)}):")
    for item in items:
        console.print(f"  • [{style}]{item}[/{style}]")


@app.command("email")
def email_cmd(
    text: Optional[str] = typer.Argument(None),
    file: Optional[Path] = typer.Option(None, "--file", "-f"),
) -> None:
    """استخراج ایمیل‌ها."""
    _print_list(" ایمیل‌ها", extract_emails(_read(text, file)))


@app.command("url")
def url_cmd(
    text: Optional[str] = typer.Argument(None),
    file: Optional[Path] = typer.Option(None, "--file", "-f"),
) -> None:
    """استخراج URLها."""
    _print_list(" URLها", extract_urls(_read(text, file)), style="cyan")


@app.command("number")
def number_cmd(
    text: Optional[str] = typer.Argument(None),
    file: Optional[Path] = typer.Option(None, "--file", "-f"),
) -> None:
    """استخراج اعداد."""
    _print_list(" اعداد", extract_numbers(_read(text, file)))


@app.command("hashtag")
def hashtag_cmd(
    text: Optional[str] = typer.Argument(None),
    file: Optional[Path] = typer.Option(None, "--file", "-f"),
) -> None:
    """استخراج هشتگ‌ها."""
    _print_list("🏷  هشتگ‌ها", extract_hashtags(_read(text, file)))


@app.command("mention")
def mention_cmd(
    text: Optional[str] = typer.Argument(None),
    file: Optional[Path] = typer.Option(None, "--file", "-f"),
) -> None:
    """استخراج منشن‌ها."""
    _print_list(" منشن‌ها", extract_mentions(_read(text, file)))


@app.command("ip")
def ip_cmd(
    text: Optional[str] = typer.Argument(None),
    file: Optional[Path] = typer.Option(None, "--file", "-f"),
) -> None:
    """استخراج IPv4."""
    _print_list(" IPv4", extract_ips(_read(text, file)))


@app.command("all")
def all_cmd(
    text: Optional[str] = typer.Argument(None),
    file: Optional[Path] = typer.Option(None, "--file", "-f"),
) -> None:
    """استخراج همهٔ الگوها."""
    content = _read(text, file)

    table = Table(title=" استخراج", title_style="bold cyan")
    table.add_column("نوع", style="bold")
    table.add_column("تعداد", justify="right", style="green")
    table.add_column("نمونه", style="dim")

    data = {
        "ایمیل": extract_emails(content),
        "URL": extract_urls(content),
        "عدد": extract_numbers(content),
        "هشتگ": extract_hashtags(content),
        "منشن": extract_mentions(content),
        "IPv4": extract_ips(content),
    }
    for kind, items in data.items():
        sample = ", ".join(items[:3]) if items else "—"
        table.add_row(kind, str(len(items)), sample)
    console.print(table)