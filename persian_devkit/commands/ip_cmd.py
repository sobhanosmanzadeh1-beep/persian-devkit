"""دستور pdev ip — نمایش IP و اطلاعات شبکه."""
from __future__ import annotations

import typer
from rich.console import Console
from rich.table import Table

from persian_devkit.utils.network_utils import (
    get_fqdn,
    get_hostname,
    get_local_ip,
    get_public_ip,
    resolve_hostname,
)

app = typer.Typer(help="نمایش IP و اطلاعات شبکه.", no_args_is_help=True)
console = Console()


@app.command("local")
def local_cmd() -> None:
    """نمایش IP محلی."""
    console.print(get_local_ip())


@app.command("public")
def public_cmd() -> None:
    """نمایش IP عمومی (نیاز به اینترنت)."""
    ip = get_public_ip()
    if ip is None:
        console.print("[red]✗ خطا:[/red] اتصال به سرویس‌های عمومی برقرار نشد.")
        raise typer.Exit(1)
    console.print(ip)


@app.command("info")
def info_cmd(
    show_public: bool = typer.Option(
        True, "--public/--no-public", help="نمایش IP عمومی."
    ),
) -> None:
    """نمایش کامل اطلاعات شبکه."""
    table = Table(title=" اطلاعات شبکه", title_style="bold cyan", show_header=False)
    table.add_column("شاخص", style="bold")
    table.add_column("مقدار", style="green")

    table.add_row("Hostname", get_hostname())
    table.add_row("FQDN", get_fqdn())
    table.add_row("IP محلی", get_local_ip())

    if show_public:
        public = get_public_ip()
        table.add_row("IP عمومی", public or "[yellow]در دسترس نیست[/yellow]")

    console.print(table)


@app.command("resolve")
def resolve_cmd(
    host: str = typer.Argument(..., help="نام دامنه یا هاست."),
) -> None:
    """تبدیل نام دامنه به IP."""
    try:
        ip = resolve_hostname(host)
    except ValueError as e:
        console.print(f"[red]✗ خطا:[/red] {e}")
        raise typer.Exit(1)
    console.print(f"{host} → [green]{ip}[/green]")