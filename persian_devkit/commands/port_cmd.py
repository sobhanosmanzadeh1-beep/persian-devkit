"""دستور pdev port — بررسی پورت‌ها."""
from __future__ import annotations

import typer
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn

from persian_devkit.utils.network_utils import is_port_open

app = typer.Typer(help="بررسی باز/بسته بودن پورت‌ها.", no_args_is_help=True)
console = Console()


@app.command("check")
def check_cmd(
    host: str = typer.Argument(..., help="هاست یا IP."),
    port: int = typer.Argument(..., min=1, max=65535, help="شمارهٔ پورت."),
    timeout: float = typer.Option(2.0, "--timeout", "-t", min=0.1, max=30.0),
) -> None:
    """بررسی یک پورت."""
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        transient=True,
        console=console,
    ) as progress:
        progress.add_task(f"بررسی {host}:{port}...", total=None)
        open_ = is_port_open(host, port, timeout=timeout)

    if open_:
        console.print(f"[green]✓[/green] {host}:{port} [green]باز است[/green]")
    else:
        console.print(f"[red]✗[/red] {host}:{port} [red]بسته یا فیلترشده[/red]")
        raise typer.Exit(1)


@app.command("scan")
def scan_cmd(
    host: str = typer.Argument(..., help="هاست یا IP."),
    start: int = typer.Argument(1, min=1, max=65535, help="پورت شروع."),
    end: int = typer.Argument(100, min=1, max=65535, help="پورت پایان."),
    timeout: float = typer.Option(0.5, "--timeout", "-t", min=0.1, max=10.0),
) -> None:
    """اسکن یک بازهٔ پورت."""
    if start > end:
        console.print("[red]✗ خطا:[/red] بازهٔ نامعتبر.")
        raise typer.Exit(1)
    if end - start > 1000:
        console.print("[red]✗ خطا:[/red] بازه حداکثر ۱۰۰۰ پورت.")
        raise typer.Exit(1)

    open_ports: list[int] = []
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task(
            f"اسکن {host} پورت {start}-{end}...", total=end - start + 1
        )
        for p in range(start, end + 1):
            if is_port_open(host, p, timeout=timeout):
                open_ports.append(p)
            progress.advance(task)

    if not open_ports:
        console.print(f"[yellow]هیچ پورت بازی یافت نشد.[/yellow]")
        return

    console.print(f"[green]✓ پورت‌های باز ({len(open_ports)}):[/green]")
    for p in open_ports:
        console.print(f"  • {p}")