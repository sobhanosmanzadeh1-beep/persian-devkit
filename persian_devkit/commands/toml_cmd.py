"""دستور pdev toml — کار با فایل‌های TOML."""
from __future__ import annotations

from pathlib import Path
from typing import Optional

import typer
from rich.console import Console

from persian_devkit.utils.data_utils import (
    dump_json,
    dump_toml,
    parse_json,
    parse_toml,
    read_text,
    write_text,
)

app = typer.Typer(help="کار با فایل‌های TOML.", no_args_is_help=True)
console = Console()


def _fail(msg: str) -> None:
    console.print(f"[red]✗ خطا:[/red] {msg}")
    raise typer.Exit(1)


@app.command("validate")
def validate_cmd(
    path: Path = typer.Argument(..., help="مسیر فایل TOML."),
) -> None:
    """بررسی صحت TOML."""
    if not path.exists():
        _fail(f"فایل یافت نشد: {path}")
    try:
        parse_toml(read_text(path))
    except ValueError as e:
        _fail(str(e))
    console.print("[green]✓ TOML معتبر است.[/green]")


@app.command("to-json")
def to_json_cmd(
    path: Path = typer.Argument(..., help="مسیر فایل TOML."),
    output: Optional[Path] = typer.Option(None, "--output", "-o"),
    indent: int = typer.Option(2, "--indent", "-i", min=0, max=10),
) -> None:
    """تبدیل TOML به JSON."""
    if not path.exists():
        _fail(f"فایل یافت نشد: {path}")
    try:
        data = parse_toml(read_text(path))
    except ValueError as e:
        _fail(str(e))
    text = dump_json(data, indent=indent)
    if output:
        write_text(output, text)
        console.print(f"[green]✓ ذخیره شد:[/green] {output}")
    else:
        console.print(text, highlight=False)


@app.command("from-json")
def from_json_cmd(
    path: Path = typer.Argument(..., help="مسیر فایل JSON."),
    output: Optional[Path] = typer.Option(None, "--output", "-o"),
) -> None:
    """تبدیل JSON به TOML."""
    if not path.exists():
        _fail(f"فایل یافت نشد: {path}")
    try:
        data = parse_json(read_text(path))
    except ValueError as e:
        _fail(str(e))
    if not isinstance(data, dict):
        _fail("ساختار سطح اول JSON باید object باشد.")
    try:
        text = dump_toml(data)
    except ValueError as e:
        _fail(str(e))
    if output:
        write_text(output, text)
        console.print(f"[green]✓ ذخیره شد:[/green] {output}")
    else:
        console.print(text, highlight=False)