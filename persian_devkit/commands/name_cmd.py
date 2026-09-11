"""دستور pdev name — تولید نام، ایمیل و داده‌های نمونهٔ فارسی."""
from __future__ import annotations

import json

import typer
from rich.console import Console
from rich.table import Table

from persian_devkit.utils.fake_utils import (
    random_city,
    random_email,
    random_first_name,
    random_full_name,
    random_last_name,
)

app = typer.Typer(help="تولید نام و داده‌های نمونهٔ فارسی.", no_args_is_help=True)
console = Console()


@app.command("full")
def full_cmd(
    count: int = typer.Option(1, "--count", "-c", min=1, max=200),
    gender: str = typer.Option("any", "--gender", "-g", help="any|male|female"),
) -> None:
    """تولید نام و نام خانوادگی."""
    if gender not in ("any", "male", "female"):
        console.print(f"[red]✗ خطا:[/red] gender نامعتبر: {gender}")
        raise typer.Exit(1)
    for _ in range(count):
        console.print(random_full_name(gender))


@app.command("first")
def first_cmd(
    count: int = typer.Option(1, "--count", "-c", min=1, max=200),
    gender: str = typer.Option("any", "--gender", "-g"),
) -> None:
    """تولید نام کوچک."""
    for _ in range(count):
        console.print(random_first_name(gender))


@app.command("last")
def last_cmd(
    count: int = typer.Option(1, "--count", "-c", min=1, max=200),
) -> None:
    """تولید نام خانوادگی."""
    for _ in range(count):
        console.print(random_last_name())


@app.command("city")
def city_cmd(
    count: int = typer.Option(1, "--count", "-c", min=1, max=200),
) -> None:
    """تولید نام شهر ایرانی."""
    for _ in range(count):
        console.print(random_city())


@app.command("email")
def email_cmd(
    count: int = typer.Option(1, "--count", "-c", min=1, max=200),
) -> None:
    """تولید ایمیل نمونه."""
    for _ in range(count):
        console.print(random_email())


@app.command("profile")
def profile_cmd(
    count: int = typer.Option(1, "--count", "-c", min=1, max=100),
    output_json: bool = typer.Option(False, "--json", "-j", help="خروجی JSON."),
) -> None:
    """پروفایل کامل نمونه (نام، ایمیل، شهر)."""
    profiles = [
        {
            "name": random_full_name(),
            "email": random_email(),
            "city": random_city(),
        }
        for _ in range(count)
    ]

    if output_json:
        console.print(json.dumps(profiles, ensure_ascii=False, indent=2), highlight=False)
        return

    table = Table(title="👤 پروفایل‌های نمونه", title_style="bold cyan")
    table.add_column("#", style="dim")
    table.add_column("نام", style="bold")
    table.add_column("ایمیل")
    table.add_column("شهر")
    for i, p in enumerate(profiles, 1):
        table.add_row(str(i), p["name"], p["email"], p["city"])
    console.print(table)