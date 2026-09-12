"""دستور pdev audio — متادیتای فایل‌های صوتی."""
from __future__ import annotations

from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.table import Table

from persian_devkit.utils.audio_utils import (
    audio_info,
    audio_tags,
    extract_cover,
)

app = typer.Typer(help="متادیتای فایل‌های صوتی (MP3, FLAC, M4A).", no_args_is_help=True)
console = Console()


def _fail(msg: str) -> None:
    console.print(f"[red]✗ خطا:[/red] {msg}")
    raise typer.Exit(1)


def _human_size(n: int) -> str:
    value = float(n)
    for unit in ("B", "KB", "MB", "GB"):
        if value < 1024:
            return f"{value:.1f} {unit}"
        value /= 1024
    return f"{value:.1f} TB"


@app.command("info")
def info_cmd(
    path: Path = typer.Argument(..., help="مسیر فایل صوتی."),
) -> None:
    """اطلاعات کامل فایل صوتی."""
    try:
        info = audio_info(path)
    except (ValueError, RuntimeError) as e:
        _fail(str(e))

    # بخش اصلی
    table = Table(title=f"🎵 {path.name}", title_style="bold cyan", show_header=False)
    table.add_column("شاخص", style="bold")
    table.add_column("مقدار", style="green")
    table.add_row("فرمت", info["format"])
    table.add_row("حجم", _human_size(info["size_bytes"]))
    table.add_row("مدت", info["duration_fmt"])
    if info["bitrate"]:
        table.add_row("بیتریت", f"{info['bitrate'] // 1000} kbps")
    if info["sample_rate"]:
        table.add_row("نرخ نمونه", f"{info['sample_rate']} Hz")
    if info["channels"]:
        table.add_row("کانال‌ها", str(info["channels"]))
    console.print(table)

    # تگ‌ها
    tags = audio_tags(path)
    if tags:
        t = Table(title="🏷  تگ‌ها", title_style="bold cyan", show_header=False)
        t.add_column("کلید", style="bold")
        t.add_column("مقدار", style="green")
        for key, value in tags.items():
            t.add_row(key, value)
        console.print(t)


@app.command("tags")
def tags_cmd(
    path: Path = typer.Argument(..., help="مسیر فایل صوتی."),
) -> None:
    """تگ‌های اصلی فایل صوتی."""
    try:
        tags = audio_tags(path)
    except (ValueError, RuntimeError) as e:
        _fail(str(e))

    if not tags:
        console.print("[yellow]⚠ تگی یافت نشد.[/yellow]")
        return

    for key, value in tags.items():
        console.print(f"[bold]{key}:[/bold] {value}")


@app.command("cover")
def cover_cmd(
    path: Path = typer.Argument(..., help="مسیر فایل صوتی."),
    output: Optional[Path] = typer.Option(
        None, "--output", "-o", help="مسیر فایل تصویر خروجی."
    ),
) -> None:
    """استخراج تصویر جلد آلبوم."""
    if output is None:
        output = path.with_suffix(".jpg")

    try:
        result = extract_cover(path, output)
    except (ValueError, RuntimeError) as e:
        _fail(str(e))

    if result is None:
        console.print("[yellow]⚠ تصویر جلدی در فایل نیست.[/yellow]")
        raise typer.Exit(1)

    console.print(f"[green]✓ ذخیره شد:[/green] {result}")