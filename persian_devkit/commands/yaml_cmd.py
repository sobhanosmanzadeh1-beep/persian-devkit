"""دستور pdev yaml — کار با فایل‌های YAML."""
from __future__ import annotations

from pathlib import Path
from typing import Any, Optional

import typer
from rich.console import Console

from persian_devkit.utils.data_utils import (
    dump_json,
    dump_yaml,
    parse_json,
    parse_yaml,
    read_text,
    write_text,
)

app = typer.Typer(help="کار با فایل‌های YAML.", no_args_is_help=True)
console = Console()


def _fail(msg: str) -> None:
    console.print(f"[red]✗ خطا:[/red] {msg}")
    raise typer.Exit(1)


def _load(path: Path) -> Any:
    if not path.exists():
        _fail(f"فایل یافت نشد: {path}")
    try:
        return parse_yaml(read_text(path))
    except ValueError as e:
        _fail(str(e))


@app.command("pretty")
def pretty_cmd(
    path: Path = typer.Argument(..., help="مسیر فایل YAML."),
    output: Optional[Path] = typer.Option(None, "--output", "-o"),
) -> None:
    """زیباسازی فایل YAML."""
    data = _load(path)
    text = dump_yaml(data)
    if output:
        write_text(output, text)
        console.print(f"[green]✓ ذخیره شد:[/green] {output}")
    else:
        console.print(text, highlight=False)


@app.command("validate")
def validate_cmd(
    path: Path = typer.Argument(..., help="مسیر فایل YAML."),
) -> None:
    """بررسی صحت YAML."""
    _load(path)
    console.print("[green]✓ YAML معتبر است.[/green]")


@app.command("to-json")
def to_json_cmd(
    path: Path = typer.Argument(..., help="مسیر فایل YAML."),
    output: Optional[Path] = typer.Option(None, "--output", "-o"),
    indent: int = typer.Option(2, "--indent", "-i", min=0, max=10),
) -> None:
    """تبدیل YAML به JSON."""
    data = _load(path)
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
    """تبدیل JSON به YAML."""
    if not path.exists():
        _fail(f"فایل یافت نشد: {path}")
    try:
        data = parse_json(read_text(path))
    except ValueError as e:
        _fail(str(e))
    text = dump_yaml(data)
    if output:
        write_text(output, text)
        console.print(f"[green]✓ ذخیره شد:[/green] {output}")
    else:
        console.print(text, highlight=False)