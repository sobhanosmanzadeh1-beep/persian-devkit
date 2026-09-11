"""دستور pdev env — کار با فایل‌های .env."""
from __future__ import annotations

from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.table import Table

from persian_devkit.utils.data_utils import dump_env, parse_env, write_text

app = typer.Typer(help="کار با فایل‌های .env.", no_args_is_help=True)
console = Console()


def _fail(msg: str) -> None:
    console.print(f"[red]✗ خطا:[/red] {msg}")
    raise typer.Exit(1)


def _load(path: Path) -> dict[str, str]:
    if not path.exists():
        _fail(f"فایل یافت نشد: {path}")
    return parse_env(path.read_text(encoding="utf-8"))


@app.command("show")
def show_cmd(
    path: Path = typer.Argument(Path(".env"), help="مسیر فایل env."),
    reveal: bool = typer.Option(
        False, "--reveal", "-r", help="نمایش مقادیر (پیش‌فرض مخفی)."
    ),
) -> None:
    """نمایش متغیرهای .env (مقادیر به‌صورت پیش‌فرض مخفی)."""
    data = _load(path)
    if not data:
        console.print("[yellow] فایل خالی است.[/yellow]")
        return

    table = Table(title=f" {path.name}", title_style="bold cyan")
    table.add_column("کلید", style="bold")
    table.add_column("مقدار")
    for k, v in data.items():
        if not reveal and any(s in k.upper() for s in ("PASS", "TOKEN", "SECRET", "KEY")):
            v = "***"
        table.add_row(k, v)
    console.print(table)


@app.command("get")
def get_cmd(
    key: str = typer.Argument(..., help="نام متغیر."),
    path: Path = typer.Option(Path(".env"), "--file", "-f", help="مسیر فایل env."),
) -> None:
    """خواندن یک متغیر خاص."""
    data = _load(path)
    if key not in data:
        console.print(f"[red]✗ خطا:[/red] متغیر یافت نشد: {key}")
        raise typer.Exit(1)
    console.print(data[key])


@app.command("to-json")
def to_json_cmd(
    path: Path = typer.Argument(Path(".env"), help="مسیر فایل env."),
) -> None:
    """تبدیل .env به JSON."""
    import json

    data = _load(path)
    console.print(json.dumps(data, ensure_ascii=False, indent=2), highlight=False)


@app.command("to-shell")
def to_shell_cmd(
    path: Path = typer.Argument(Path(".env"), help="مسیر فایل env."),
    export: bool = typer.Option(True, "--export/--no-export"),
) -> None:
    """تبدیل .env به دستورات export برای bash/zsh."""
    data = _load(path)
    prefix = "export " if export else ""
    for k, v in data.items():
        console.print(f"{prefix}{k}={v!r}")


@app.command("sort")
def sort_cmd(
    path: Path = typer.Argument(..., help="مسیر فایل env."),
    output: Optional[Path] = typer.Option(None, "--output", "-o"),
) -> None:
    """مرتب‌سازی کلیدهای .env به ترتیب الفبا."""
    data = _load(path)
    sorted_data = dict(sorted(data.items()))
    text = dump_env(sorted_data)
    if output:
        write_text(output, text)
        console.print(f"[green] ذخیره شد:[/green] {output}")
    else:
        console.print(text, highlight=False)