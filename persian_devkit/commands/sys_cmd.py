"""دستور pdev sys — اطلاعات سیستم."""
from __future__ import annotations

from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.table import Table

from persian_devkit.utils.system_utils import (
    cpu_info,
    disk_info,
    format_bytes,
    memory_info,
    python_info,
    top_processes,
    uptime,
)

app = typer.Typer(help="اطلاعات سیستم.", no_args_is_help=True)
console = Console()


def _fail(msg: str) -> None:
    console.print(f"[red]✗ خطا:[/red] {msg}")
    raise typer.Exit(1)


@app.command("all")
def all_cmd() -> None:
    """نمایش همهٔ اطلاعات سیستم."""
    info = python_info()

    table = Table(title=" اطلاعات سیستم", title_style="bold cyan", show_header=False)
    table.add_column("شاخص", style="bold")
    table.add_column("مقدار", style="green")
    table.add_row("سیستم عامل", f"{info['system']} {info['release']}")
    table.add_row("معماری", info["architecture"])
    table.add_row("پردازنده", info["processor"][:50] or "—")
    table.add_row("پایتون", f"{info['python_version']} ({info['python_impl']})")
    table.add_row("مسیر پایتون", info["executable"])
    console.print(table)

    # RAM
    try:
        mem = memory_info()
        table = Table(title=" حافظه", title_style="bold cyan", show_header=False)
        table.add_column("شاخص", style="bold")
        table.add_column("مقدار", style="green")
        table.add_row("کل", format_bytes(mem["total"]))
        table.add_row("استفاده‌شده", f"{format_bytes(mem['used'])} ({mem['percent']}%)")
        table.add_row("آزاد", format_bytes(mem["available"]))
        console.print(table)
    except RuntimeError as e:
        console.print(f"[yellow] {e}[/yellow]")

    # CPU
    try:
        cpu = cpu_info()
        table = Table(title="  پردازنده", title_style="bold cyan", show_header=False)
        table.add_column("شاخص", style="bold")
        table.add_column("مقدار", style="green")
        table.add_row("هستهٔ فیزیکی", str(cpu["physical_cores"]))
        table.add_row("هستهٔ منطقی", str(cpu["logical_cores"]))
        table.add_row("بار فعلی", f"{cpu['percent']}%")
        if cpu["freq_current"]:
            table.add_row("فرکانس", f"{cpu['freq_current']:.0f} MHz")
        console.print(table)
    except RuntimeError as e:
        console.print(f"[yellow]⚠ {e}[/yellow]")

    # Uptime
    try:
        up = uptime()
        hours, remainder = divmod(int(up.total_seconds()), 3600)
        minutes = remainder // 60
        console.print(f"\n[bold]⏱  روشن بودن:[/bold] {hours} ساعت و {minutes} دقیقه")
    except RuntimeError:
        pass


@app.command("python")
def python_cmd() -> None:
    """اطلاعات پایتون."""
    info = python_info()
    for k, v in info.items():
        console.print(f"[bold]{k}:[/bold] {v}")


@app.command("disk")
def disk_cmd(
    path: Optional[Path] = typer.Argument(None, help="مسیر (پیش‌فرض: ریشه)."),
) -> None:
    """اطلاعات دیسک."""
    try:
        info = disk_info(path)
    except RuntimeError as e:
        _fail(str(e))

    table = Table(title=f"💾 دیسک: {info['path']}", title_style="bold cyan", show_header=False)
    table.add_column("شاخص", style="bold")
    table.add_column("مقدار", style="green")
    table.add_row("کل", format_bytes(info["total"]))
    table.add_row("استفاده‌شده", f"{format_bytes(info['used'])} ({info['percent']}%)")
    table.add_row("آزاد", format_bytes(info["free"]))
    console.print(table)


@app.command("memory")
def memory_cmd() -> None:
    """اطلاعات حافظه."""
    try:
        info = memory_info()
    except RuntimeError as e:
        _fail(str(e))

    table = Table(title="🧠 حافظه", title_style="bold cyan", show_header=False)
    table.add_column("شاخص", style="bold")
    table.add_column("مقدار", style="green")
    table.add_row("کل", format_bytes(info["total"]))
    table.add_row("استفاده‌شده", f"{format_bytes(info['used'])} ({info['percent']}%)")
    table.add_row("آزاد", format_bytes(info["available"]))
    table.add_row("Swap کل", format_bytes(info["swap_total"]))
    table.add_row("Swap استفاده", f"{format_bytes(info['swap_used'])} ({info['swap_percent']}%)")
    console.print(table)


@app.command("cpu")
def cpu_cmd() -> None:
    """اطلاعات پردازنده."""
    try:
        info = cpu_info()
    except RuntimeError as e:
        _fail(str(e))

    table = Table(title="⚙️  پردازنده", title_style="bold cyan", show_header=False)
    table.add_column("شاخص", style="bold")
    table.add_column("مقدار", style="green")
    table.add_row("هستهٔ فیزیکی", str(info["physical_cores"]))
    table.add_row("هستهٔ منطقی", str(info["logical_cores"]))
    table.add_row("بار فعلی", f"{info['percent']}%")
    if info["freq_current"]:
        table.add_row("فرکانس فعلی", f"{info['freq_current']:.0f} MHz")
    if info["freq_max"]:
        table.add_row("حداکثر فرکانس", f"{info['freq_max']:.0f} MHz")
    console.print(table)


@app.command("uptime")
def uptime_cmd() -> None:
    """مدت زمان روشن بودن سیستم."""
    try:
        up = uptime()
    except RuntimeError as e:
        _fail(str(e))

    days = up.days
    hours, rem = divmod(up.seconds, 3600)
    minutes = rem // 60
    parts: list[str] = []
    if days:
        parts.append(f"{days} روز")
    if hours:
        parts.append(f"{hours} ساعت")
    if minutes:
        parts.append(f"{minutes} دقیقه")
    console.print(" و ".join(parts) if parts else "کمتر از یک دقیقه")


@app.command("top")
def top_cmd(
    limit: int = typer.Option(10, "--limit", "-n", min=1, max=50, help="تعداد."),
    by: str = typer.Option("cpu", "--by", "-b", help="مرتب‌سازی: cpu یا memory."),
) -> None:
    """پرمصرف‌ترین پردازش‌ها."""
    try:
        procs = top_processes(limit=limit, by=by)
    except (RuntimeError, ValueError) as e:
        _fail(str(e))

    if not procs:
        console.print("[yellow]⚠ پردازشی یافت نشد.[/yellow]")
        return

    table = Table(title=f"🔝 پرمصرف‌ترین پردازش‌ها (by {by})", title_style="bold cyan")
    table.add_column("PID", style="dim", justify="right")
    table.add_column("نام", style="bold")
    table.add_column("CPU %", justify="right")
    table.add_column("RAM %", justify="right")
    for p in procs:
        table.add_row(str(p["pid"]), p["name"][:40], f"{p['cpu']}", f"{p['memory']}")
    console.print(table)