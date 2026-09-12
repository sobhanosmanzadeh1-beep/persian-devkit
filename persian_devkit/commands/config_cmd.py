"""دستور pdev config — مدیریت تنظیمات."""
from __future__ import annotations

from typing import Any

import typer
from rich.console import Console
from rich.table import Table

from persian_devkit.utils.config_utils import (
    CONFIG_FILE,
    DEFAULT_CONFIG,
    get_value,
    load_config,
    reset_config,
    save_config,
    set_value,
)

app = typer.Typer(help="مدیریت تنظیمات pdev.", no_args_is_help=True)
console = Console()


def _parse_value(value: str) -> Any:
    """تبدیل رشته به نوع مناسب (bool/int/float/str)."""
    low = value.lower()
    if low == "true":
        return True
    if low == "false":
        return False
    try:
        return int(value)
    except ValueError:
        pass
    try:
        return float(value)
    except ValueError:
        pass
    return value


@app.command("path")
def path_cmd() -> None:
    """مسیر فایل تنظیمات."""
    console.print(str(CONFIG_FILE))


@app.command("show")
def show_cmd() -> None:
    """نمایش کل تنظیمات."""
    console.print_json(data=load_config())


@app.command("get")
def get_cmd(
    key: str = typer.Argument(..., help="کلید با dot notation، مثل shell.banner"),
) -> None:
    """خواندن یک کلید."""
    value = get_value(key)
    if value is None:
        console.print(f"[yellow]⚠ کلید یافت نشد:[/yellow] {key}")
        raise typer.Exit(1)
    console.print(str(value))


@app.command("set")
def set_cmd(
    key: str = typer.Argument(..., help="کلید (dot notation)."),
    value: str = typer.Argument(..., help="مقدار (خودکار نوع تشخیص داده می‌شود)."),
) -> None:
    """نوشتن یک مقدار."""
    parsed = _parse_value(value)
    set_value(key, parsed)
    console.print(f"[green]✓[/green] {key} = {parsed!r}")


@app.command("init")
def init_cmd(
    force: bool = typer.Option(False, "--force", "-f", help="بازنویسی فایل موجود."),
) -> None:
    """ساخت فایل تنظیمات با مقادیر پیش‌فرض."""
    if CONFIG_FILE.exists() and not force:
        console.print(
            f"[yellow]⚠ فایل موجود است:[/yellow] {CONFIG_FILE} (از --force استفاده کن)"
        )
        raise typer.Exit(1)
    save_config(dict(DEFAULT_CONFIG))
    console.print(f"[green]✓ ذخیره شد:[/green] {CONFIG_FILE}")


@app.command("reset")
def reset_cmd() -> None:
    """حذف فایل تنظیمات (بازگشت به پیش‌فرض)."""
    if not CONFIG_FILE.exists():
        console.print("[yellow]فایلی وجود ندارد.[/yellow]")
        return
    reset_config()
    console.print("[green]✓ حذف شد.[/green]")


@app.command("keys")
def keys_cmd() -> None:
    """نمایش همهٔ کلیدهای موجود."""
    cfg = load_config()

    def _walk(data: dict, prefix: str = "") -> list[tuple[str, Any]]:
        result: list[tuple[str, Any]] = []
        for k, v in data.items():
            key = f"{prefix}.{k}" if prefix else k
            if isinstance(v, dict):
                result.extend(_walk(v, key))
            else:
                result.append((key, v))
        return result

    table = Table(title="  کلیدهای تنظیمات", title_style="bold cyan")
    table.add_column("کلید", style="bold")
    table.add_column("مقدار", style="green")
    for key, value in _walk(cfg):
        table.add_row(key, repr(value))
    console.print(table)