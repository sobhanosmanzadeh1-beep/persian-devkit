"""دستور pdev info — اطلاعات کامل pdev و سیستم."""
from __future__ import annotations

import platform
import sys
from pathlib import Path

import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from persian_devkit import __version__

console = Console()


def _count_commands() -> int:
    """تعداد کل دستورات pdev."""
    from persian_devkit.main import app

    count = 0
    for _ in app.registered_commands:
        count += 1
    for group in app.registered_groups:
        if group.typer_instance:
            count += len(group.typer_instance.registered_commands)
    return count


def _count_subcommands() -> dict[str, int]:
    """تعداد زیرفرمان‌های هر گروه."""
    from persian_devkit.main import app

    result: dict[str, int] = {}
    for group in app.registered_groups:
        name = group.name or "?"
        if group.typer_instance:
            result[name] = len(group.typer_instance.registered_commands)
    return result


def info_command(
    verbose: bool = typer.Option(
        False, "--verbose", "-v", help="نمایش لیست همهٔ دستورات."
    ),
) -> None:
    """اطلاعات کامل pdev و سیستم."""
    # بخش ۱: pdev
    console.print(
        Panel(
            f"[bold cyan] persian-devkit[/bold cyan]\n"
            f"نسخه: [green]{__version__}[/green]\n"
            f"مسیر نصب: [dim]{Path(__file__).parent.parent}[/dim]",
            title="پکیج",
            expand=False,
        )
    )

    # بخش ۲: Python
    py_table = Table(title=" Python", title_style="bold cyan", show_header=False)
    py_table.add_column("شاخص", style="bold")
    py_table.add_column("مقدار", style="green")
    py_table.add_row("نسخه", sys.version.split()[0])
    py_table.add_row("پیاده‌سازی", platform.python_implementation())
    py_table.add_row("مسیر", sys.executable)
    console.print(py_table)

    # بخش ۳: سیستم
    sys_table = Table(title=" سیستم", title_style="bold cyan", show_header=False)
    sys_table.add_column("شاخص", style="bold")
    sys_table.add_column("مقدار", style="green")
    sys_table.add_row("سیستم‌عامل", f"{platform.system()} {platform.release()}")
    sys_table.add_row("معماری", platform.machine())
    sys_table.add_row("پلتفرم", platform.platform())
    console.print(sys_table)

    # بخش ۴: آمار
    try:
        total = _count_commands()
        subcommands = _count_subcommands()
        groups = len(subcommands)
        total_subs = sum(subcommands.values())

        stat_table = Table(
            title=" آمار", title_style="bold cyan", show_header=False
        )
        stat_table.add_column("شاخص", style="bold")
        stat_table.add_column("مقدار", style="green")
        stat_table.add_row("دستورات اصلی", str(total))
        stat_table.add_row("گروه‌ها", str(groups))
        stat_table.add_row("زیرفرمان‌ها", str(total_subs))
        stat_table.add_row("مجموع", str(total + total_subs))
        console.print(stat_table)

        if verbose:
            sub_table = Table(title=" زیرفرمان‌ها", title_style="bold cyan")
            sub_table.add_column("گروه", style="bold")
            sub_table.add_column("تعداد", justify="right", style="green")
            for name, count in sorted(subcommands.items()):
                sub_table.add_row(name, str(count))
            console.print(sub_table)
    except Exception as exc:
        console.print(f"[yellow]⚠ نمی‌توان آمار را محاسبه کرد: {exc}[/yellow]")

    # بخش ۵: لینک‌ها
    console.print(
        Panel(
            "[bold] لینک‌ها[/bold]\n"
            "PyPI:    [cyan]https://pypi.org/project/persian-devkit/[/cyan]\n"
            "GitHub:  [cyan]https://github.com/sobhanosmanzadeh1-beep/persian-devkit[/cyan]\n"
            "Issues:  [cyan]https://github.com/sobhanosmanzadeh1-beep/persian-devkit/issues[/cyan]",
            expand=False,
        )
    )