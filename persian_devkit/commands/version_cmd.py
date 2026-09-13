"""دستور pdev version — نمایش اطلاعات دقیق نسخه."""
from __future__ import annotations

import sys

import typer
from rich.console import Console
from rich.table import Table

from persian_devkit import __version__

console = Console()


def version_command(
    short: bool = typer.Option(False, "--short", "-s", help="خروجی کوتاه."),
) -> None:
    """نمایش اطلاعات دقیق نسخه.

    مثال:
      pdev version          # کامل
      pdev version --short  # فقط شمارهٔ نسخه
    """
    if short:
        console.print(__version__)
        return

    table = Table(show_header=False, box=None)
    table.add_column(style="bold")
    table.add_column(style="green")
    table.add_row("نسخه", __version__)
    table.add_row("پایتون", sys.version.split()[0])
    table.add_row("سیستم‌عامل", sys.platform)
    console.print(table)