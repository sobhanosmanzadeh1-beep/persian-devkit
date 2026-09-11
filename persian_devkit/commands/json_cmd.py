"""دستور `pdev json` — کار با فایل‌های JSON."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Optional

import typer
from rich.console import Console

app = typer.Typer(help="کار با فایل‌های JSON.", no_args_is_help=True)
console = Console()


def _fail(message: str) -> None:
    console.print(f"[red]✗ خطا:[/red] {message}")
    raise typer.Exit(1)


def _load(path: Path) -> Any:
    """فایل JSON را می‌خواند و پارس می‌کند."""
    try:
        raw = path.read_text(encoding="utf-8")
    except FileNotFoundError:
        _fail(f"فایل یافت نشد: {path}")
    except OSError as e:
        _fail(f"خطا در خواندن فایل: {e}")
    try:
        return json.loads(raw)
    except json.JSONDecodeError as e:
        _fail(f"JSON نامعتبر: {e}")


def _is_quiet(ctx: typer.Context) -> bool:
    """آیا حالت quiet فعال است؟"""
    try:
        return bool(ctx.obj and ctx.obj.get("quiet"))
    except Exception:
        return False


@app.command("pretty")
def pretty_cmd(
    ctx: typer.Context,
    path: Path = typer.Argument(..., help="مسیر فایل JSON."),
    indent: int = typer.Option(2, "--indent", "-i", min=0, max=10, help="تعداد فاصله."),
    output: Optional[Path] = typer.Option(
        None, "--output", "-o", help="ذخیره در فایل خروجی."
    ),
) -> None:
    """زیباسازی JSON."""
    data = _load(path)
    text = json.dumps(data, ensure_ascii=False, indent=indent)
    if output is not None:
        output.write_text(text, encoding="utf-8")
        if not _is_quiet(ctx):
            console.print(f"[green]✓ ذخیره شد:[/green] {output}")
    else:
        console.print(text, highlight=False)


@app.command("minify")
def minify_cmd(
    ctx: typer.Context,
    path: Path = typer.Argument(..., help="مسیر فایل JSON."),
    output: Optional[Path] = typer.Option(
        None, "--output", "-o", help="ذخیره در فایل خروجی."
    ),
) -> None:
    """فشرده‌سازی JSON."""
    data = _load(path)
    text = json.dumps(data, ensure_ascii=False, separators=(",", ":"))
    if output is not None:
        output.write_text(text, encoding="utf-8")
        if not _is_quiet(ctx):
            console.print(f"[green]✓ ذخیره شد:[/green] {output}")
    else:
        console.print(text, highlight=False)


@app.command("validate")
def validate_cmd(
    ctx: typer.Context,
    path: Path = typer.Argument(..., help="مسیر فایل JSON."),
) -> None:
    """بررسی صحت ساختار JSON."""
    try:
        raw = path.read_text(encoding="utf-8")
    except FileNotFoundError:
        _fail(f"فایل یافت نشد: {path}")
    try:
        json.loads(raw)
    except json.JSONDecodeError as e:
        _fail(f"JSON نامعتبر است: {e}")
    if not _is_quiet(ctx):
        console.print("[green]✓ JSON معتبر است.[/green]")


@app.command("keys")
def keys_cmd(
    path: Path = typer.Argument(..., help="مسیر فایل JSON."),
) -> None:
    """نمایش کلیدهای سطح اول."""
    data = _load(path)
    if not isinstance(data, dict):
        console.print("[yellow]⚠ هشدار:[/yellow] ساختار سطح اول شیء (object) نیست.")
        raise typer.Exit(1)
    for key in data.keys():
        console.print(f"• {key}")


def _flatten(obj: Any, prefix: str = "") -> dict[str, Any]:
    """مسطح‌سازی JSON تودرتو به کلیدهای نقطه‌ای."""
    result: dict[str, Any] = {}
    if isinstance(obj, dict):
        for key, value in obj.items():
            new_key = f"{prefix}.{key}" if prefix else str(key)
            result.update(_flatten(value, new_key))
    elif isinstance(obj, list):
        for idx, value in enumerate(obj):
            new_key = f"{prefix}[{idx}]"
            result.update(_flatten(value, new_key))
    else:
        result[prefix] = obj
    return result


@app.command("flatten")
def flatten_cmd(
    path: Path = typer.Argument(..., help="مسیر فایل JSON."),
) -> None:
    """مسطح‌سازی JSON تودرتو به کلیدهای نقطه‌ای."""
    data = _load(path)
    flat = _flatten(data)
    console.print(json.dumps(flat, ensure_ascii=False, indent=2), highlight=False)