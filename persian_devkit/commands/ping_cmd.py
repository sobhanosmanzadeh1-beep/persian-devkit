"""دستور pdev ping — بررسی دسترس‌پذیری هاست."""
from __future__ import annotations

import typer
from rich.console import Console

from persian_devkit.utils.network_utils import ping_host, resolve_hostname

app = typer.Typer(help="بررسی دسترس‌پذیری هاست.", no_args_is_help=True)
console = Console()


@app.command("host")
def host_cmd(
    host: str = typer.Argument(..., help="هاست یا IP."),
    count: int = typer.Option(4, "--count", "-c", min=1, max=20, help="تعداد بسته."),
    timeout: int = typer.Option(5, "--timeout", "-t", min=1, max=30, help="ثانیه."),
) -> None:
    """ارسال ping به یک هاست."""
    # اول resolve کن تا خطای واضح بدهد
    try:
        ip = resolve_hostname(host)
    except ValueError as e:
        console.print(f"[red]✗ خطا:[/red] {e}")
        raise typer.Exit(1)

    if ip != host:
        console.print(f"[dim]Resolving {host} → {ip}[/dim]\n")

    result = ping_host(host, count=count, timeout=timeout)

    if result["error"] == "ping-not-found":
        console.print(
            "[red]✗ خطا:[/red] دستور ping روی سیستم یافت نشد.\n"
            "[yellow]نکته:[/yellow] روی بعضی سیستم‌ها نیاز به نصب دستی دارد."
        )
        raise typer.Exit(1)

    if result["error"] == "timeout":
        console.print("[red]✗ timeout:[/red] پاسخی دریافت نشد.")
        raise typer.Exit(1)

    console.print(result["output"], highlight=False, markup=False)

    if not result["success"]:
        raise typer.Exit(1)