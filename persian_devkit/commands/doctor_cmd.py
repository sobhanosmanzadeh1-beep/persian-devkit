"""دستور pdev doctor — بررسی سلامت نصب و محیط."""
from __future__ import annotations

import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from persian_devkit.utils.doctor_utils import run_all_checks, summary

console = Console()


_STATUS_ICONS = {
    "ok": "[green]✓[/green]",
    "warn": "[yellow]⚠[/yellow]",
    "fail": "[red]✗[/red]",
}


def doctor_command(
    fix_hints: bool = typer.Option(
        True, "--hints/--no-hints", help="نمایش راه‌حل برای مشکلات."
    ),
) -> None:
    """بررسی سلامت نصب pdev و محیط.

    این دستور:
      - نسخهٔ پایتون و سیستم‌عامل را چک می‌کند
      - وابستگی‌های اجباری و اختیاری را بررسی می‌کند
      - فایل config و پوشهٔ پلاگین‌ها را می‌سنجد
      - مجوزهای نوشتن را تست می‌کند
      - مشکلات را با راه‌حل نمایش می‌دهد
    """
    console.print(
        Panel(
            "🩺 بررسی سلامت persian-devkit",
            style="cyan",
            expand=False,
        )
    )

    results = run_all_checks()

    table = Table(show_header=True, header_style="bold")
    table.add_column("", width=3)
    table.add_column("بررسی", style="bold")
    table.add_column("وضعیت")

    for r in results:
        icon = _STATUS_ICONS.get(r.status, "?")
        table.add_row(icon, r.name, r.message)

    console.print(table)

    # خلاصه
    s = summary(results)
    summary_text = (
        f"[green]{s['ok']} موفق[/green]  "
        f"[yellow]{s['warn']} هشدار[/yellow]  "
        f"[red]{s['fail']} خطا[/red]"
    )
    console.print(f"\n[bold]خلاصه:[/bold] {summary_text} از {s['total']}")

    # راه‌حل‌ها
    if fix_hints:
        problems = [r for r in results if r.status in ("warn", "fail") and r.fix_hint]
        if problems:
            console.print("\n[bold]راه‌حل‌های پیشنهادی:[/bold]")
            for r in problems:
                style = "red" if r.status == "fail" else "yellow"
                console.print(
                    f"  [{style}]•[/{style}] [bold]{r.name}:[/bold] {r.fix_hint}"
                )

    # خروج با کد خطا اگر مشکلی بود
    if s["fail"] > 0:
        raise typer.Exit(1)