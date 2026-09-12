"""دستور pdev auto — ابزارهای خودکارسازی."""
from __future__ import annotations

from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.table import Table

from persian_devkit.utils.automation_utils import (
    explain_cron,
    parse_batch_file,
    parse_cron,
    repeat_command,
    run_batch,
    run_command,
    watch_path,
)

app = typer.Typer(help="ابزارهای خودکارسازی (تکرار، batch، پایش).", no_args_is_help=True)
console = Console()


def _fail(msg: str) -> None:
    console.print(f"[red]✗ خطا:[/red] {msg}")
    raise typer.Exit(1)


def _print_result(result) -> None:
    """نمایش یک RunResult."""
    if result.stdout:
        console.print(result.stdout.rstrip(), highlight=False, markup=False)
    if result.stderr:
        console.print(
            f"[red]{result.stderr.rstrip()}[/red]", highlight=False, markup=False
        )


#run


@app.command("run")
def run_cmd(
    command: str = typer.Argument(..., help="دستور برای اجرا."),
    timeout: Optional[float] = typer.Option(
        None, "--timeout", "-t", min=0.1, help="محدودیت زمان (ثانیه)."
    ),
) -> None:
    """اجرای یک دستور با نمایش زمان."""
    result = run_command(command, timeout=timeout)
    _print_result(result)

    if result.timed_out:
        console.print(f"[yellow]⏱  timeout پس از {timeout}s[/yellow]")
    console.print(f"[dim]زمان اجرا: {result.duration:.2f}s[/dim]")

    if not result.success:
        raise typer.Exit(result.returncode if result.returncode > 0 else 1)


#repeat


@app.command("repeat")
def repeat_cmd(
    command: str = typer.Argument(..., help="دستور برای اجرا."),
    times: int = typer.Option(1, "--times", "-n", min=1, max=10000, help="تعداد تکرار."),
    interval: float = typer.Option(
        0.0, "--interval", "-i", min=0.0, help="فاصله بین اجراها (ثانیه)."
    ),
    timeout: Optional[float] = typer.Option(
        None, "--timeout", "-t", min=0.1, help="محدودیت زمان هر اجرا."
    ),
    stop_on_error: bool = typer.Option(
        False, "--stop-on-error", "-s", help="توقف در صورت خطا."
    ),
    quiet: bool = typer.Option(False, "--quiet", "-q", help="فقط خلاصه."),
) -> None:
    """اجرای یک دستور چند بار با فاصلهٔ زمانی."""
    counter = {"success": 0, "fail": 0}

    def on_iter(i: int, result) -> None:
        if result.success:
            counter["success"] += 1
        else:
            counter["fail"] += 1
        if not quiet:
            status = "[green]✓[/green]" if result.success else "[red]✗[/red]"
            console.print(f"[dim]#{i}[/dim] {status} ({result.duration:.2f}s)")
            if result.stdout and not quiet:
                console.print(f"  {result.stdout.rstrip()}", highlight=False)

    try:
        results = repeat_command(
            command,
            times=times,
            interval=interval,
            timeout=timeout,
            stop_on_error=stop_on_error,
            on_iteration=on_iter,
        )
    except ValueError as e:
        _fail(str(e))

    total = len(results)
    console.print(
        f"\n[bold]خلاصه:[/bold] {counter['success']} موفق، "
        f"{counter['fail']} ناموفق (از {total})"
    )

    if counter["fail"] > 0:
        raise typer.Exit(1)


#batch


@app.command("batch")
def batch_cmd(
    file: Path = typer.Argument(..., help="فایل batch (هر خط یک دستور)."),
    cwd: Optional[Path] = typer.Option(None, "--cwd", help="پوشهٔ اجرا."),
) -> None:
    """اجرای چند دستور از یک فایل.

    راهنما:
      - هر خط یک دستور
      - خطوط خالی و # کامنت نادیده گرفته می‌شوند
      - با پیشوند ! خطا نادیده گرفته می‌شود
    """
    try:
        steps = parse_batch_file(file)
    except ValueError as e:
        _fail(str(e))

    if not steps:
        console.print("[yellow]⚠ فایل خالی است.[/yellow]")
        return

    success = 0
    fail = 0

    def on_step(i: int, step, result) -> None:
        nonlocal success, fail
        status = "[green]✓[/green]" if result.success else "[red]✗[/red]"
        console.print(f"{status} [bold]#{i}[/bold] {step.command}")
        if result.stdout:
            console.print(f"  [dim]{result.stdout.rstrip()}[/dim]", highlight=False)
        if not result.success and result.stderr:
            console.print(f"  [red]{result.stderr.rstrip()}[/red]", highlight=False)
        if result.success:
            success += 1
        else:
            fail += 1

    run_batch(steps, cwd=cwd, on_step=on_step)

    console.print(
        f"\n[bold]خلاصه:[/bold] {success} موفق، {fail} ناموفق (از {len(steps)})"
    )
    if fail > 0:
        raise typer.Exit(1)


#watch


@app.command("watch")
def watch_cmd(
    path: Path = typer.Argument(..., help="فایل یا پوشه برای پایش."),
    command: str = typer.Argument(..., help="دستوری که با هر تغییر اجرا می‌شود."),
    interval: float = typer.Option(1.0, "--interval", "-i", min=0.1, help="فاصلهٔ پایش."),
    count: Optional[int] = typer.Option(
        None, "--count", "-n", min=1, help="حداکثر تعداد تکرار (پیش‌فرض: بی‌نهایت)."
    ),
    timeout: Optional[float] = typer.Option(None, "--timeout", "-t"),
) -> None:
    """پایش فایل/پوشه و اجرای دستور در هر تغییر.

    برای توقف: Ctrl+C
    """
    if not path.exists():
        _fail(f"مسیر یافت نشد: {path}")

    console.print(f"[cyan]👁  پایش {path}... (Ctrl+C برای توقف)[/cyan]")
    console.print(f"[dim]دستور: {command}[/dim]")

    try:
        watch_path(
            path,
            command,
            interval=interval,
            max_iterations=count,
            timeout=timeout,
            on_change=lambda p, r: (
                console.print(f"\n[green]🔄 تغییر در {p.name}[/green]"),
                _print_result(r),
            ),
        )
    except KeyboardInterrupt:
        console.print("\n[yellow]توقف با Ctrl+C[/yellow]")
    except ValueError as e:
        _fail(str(e))


#cron


@app.command("cron")
def cron_cmd(
    expression: str = typer.Argument(..., help="عبارت cron یا preset (مثل @daily)."),
) -> None:
    """تجزیه و توضیح عبارت cron (۵ فیلد)."""
    try:
        parsed = parse_cron(expression)
    except ValueError as e:
        _fail(str(e))

    table = Table(title=f" {expression}", title_style="bold cyan")
    table.add_column("فیلد", style="bold")
    table.add_column("مقادیر", style="green")

    def fmt(values, total):
        if len(values) == total:
            return "هر مقدار"
        return ", ".join(str(v) for v in values)

    table.add_row("دقیقه", fmt(parsed["minute"], 60))
    table.add_row("ساعت", fmt(parsed["hour"], 24))
    table.add_row("روز ماه", fmt(parsed["day"], 31))
    table.add_row("ماه", fmt(parsed["month"], 12))
    table.add_row("روز هفته", fmt(parsed["weekday"], 7))
    console.print(table)

    try:
        explanation = explain_cron(expression)
        console.print(f"\n[bold] توضیح:[/bold] {explanation}")
    except ValueError:
        pass