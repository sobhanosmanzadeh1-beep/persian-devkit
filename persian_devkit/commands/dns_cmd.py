"""دستور pdev dns — جستجوی رکوردهای DNS."""
from __future__ import annotations

import typer
from rich.console import Console
from rich.table import Table

from persian_devkit.utils.dns_utils import RECORD_TYPES, lookup, reverse_lookup

app = typer.Typer(help="جستجوی رکوردهای DNS.", no_args_is_help=True)
console = Console()


@app.command("lookup")
def lookup_cmd(
    domain: str = typer.Argument(..., help="نام دامنه."),
    record_type: str = typer.Option(
        "A", "--type", "-t", help=f"نوع رکورد: {', '.join(RECORD_TYPES)}"
    ),
) -> None:
    """جستجوی یک رکورد DNS."""
    rtype = record_type.upper()
    if rtype not in RECORD_TYPES:
        console.print(
            f"[red]✗ خطا:[/red] نوع نامعتبر: {rtype}. "
            f"مجاز: {', '.join(RECORD_TYPES)}"
        )
        raise typer.Exit(1)

    try:
        results = lookup(domain, rtype)
    except ValueError as e:
        console.print(f"[red]✗ خطا:[/red] {e}")
        raise typer.Exit(1)

    if not results:
        console.print(f"[yellow]⚠ رکوردی یافت نشد.[/yellow]")
        raise typer.Exit(1)

    for r in results:
        console.print(f"  • {r}")


@app.command("all")
def all_cmd(
    domain: str = typer.Argument(..., help="نام دامنه."),
) -> None:
    """جستجوی همهٔ رکوردهای اصلی."""
    table = Table(title=f" DNS — {domain}", title_style="bold cyan")
    table.add_column("نوع", style="bold")
    table.add_column("مقدار")

    any_found = False
    for rtype in ("A", "AAAA", "CNAME", "MX", "NS"):
        try:
            results = lookup(domain, rtype)
        except ValueError:
            results = []
        if results:
            any_found = True
            for i, r in enumerate(results):
                table.add_row(rtype if i == 0 else "", r)

    if not any_found:
        console.print("[yellow]⚠ رکوردی یافت نشد.[/yellow]")
        return
    console.print(table)


@app.command("reverse")
def reverse_cmd(
    ip: str = typer.Argument(..., help="آدرس IP."),
) -> None:
    """جستجوی معکوس IP (PTR)."""
    result = reverse_lookup(ip)
    if result is None:
        console.print(f"[yellow]⚠ نتیجه‌ای یافت نشد.[/yellow]")
        raise typer.Exit(1)
    console.print(f"{ip} → [green]{result}[/green]")