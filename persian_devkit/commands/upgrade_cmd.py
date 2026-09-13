"""دستور pdev upgrade — بررسی و ارتقای pdev."""
from __future__ import annotations

import subprocess
import sys

import typer
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn

from persian_devkit.utils.version_utils import (
    current_version,
    is_newer,
    latest_version,
)

console = Console()


def upgrade_command(
    check_only: bool = typer.Option(
        False, "--check", "-c", help="فقط بررسی، بدون نصب."
    ),
    yes: bool = typer.Option(
        False, "--yes", "-y", help="بدون تأیید، ارتقا بده."
    ),
) -> None:
    """بررسی و ارتقای pdev به آخرین نسخه.

    مثال:
      pdev upgrade --check     # فقط بررسی
      pdev upgrade             # با تأیید
      pdev upgrade --yes       # بدون تأیید
    """
    current = current_version()
    console.print(f"نسخهٔ فعلی: [bold]{current}[/bold]")

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        transient=True,
        console=console,
    ) as progress:
        progress.add_task("بررسی PyPI...", total=None)
        latest = latest_version()

    if latest is None:
        console.print("[yellow]⚠ اتصال به PyPI برقرار نشد.[/yellow]")
        raise typer.Exit(1)

    console.print(f"آخرین نسخه: [bold]{latest}[/bold]")

    if not is_newer(latest, current):
        console.print(
            Panel(
                f"[green]✓ pdev به‌روز است.[/green]\nنسخهٔ نصب‌شده: {current}",
                style="green",
                expand=False,
            )
        )
        return

    console.print(
        f"\n[cyan]🎉 نسخهٔ جدید موجود است: {current} → {latest}[/cyan]"
    )

    if check_only:
        console.print("\n[dim]برای ارتقا: pdev upgrade --yes[/dim]")
        return

    if not yes:
        confirm = typer.confirm("ارتقا بده؟")
        if not confirm:
            console.print("[dim]لغو شد.[/dim]")
            return

    console.print("\n[cyan]در حال ارتقا...[/cyan]")

    cmd = [sys.executable, "-m", "pip", "install", "--upgrade", "persian-devkit"]
    try:
        result = subprocess.run(
            cmd, capture_output=True, text=True, encoding="utf-8"
        )
    except Exception as exc:
        console.print(f"[red]✗ خطا:[/red] {exc}")
        raise typer.Exit(1)

    if result.returncode == 0:
        console.print(f"[green]✓ با موفقیت به {latest} ارتقا یافت.[/green]")
        console.print("[dim]لطفاً ترمینال را ببند و دوباره باز کن.[/dim]")
    else:
        console.print("[red]✗ ارتقا ناموفق بود.[/red]")
        if result.stderr:
            console.print(result.stderr.strip())
        raise typer.Exit(1)