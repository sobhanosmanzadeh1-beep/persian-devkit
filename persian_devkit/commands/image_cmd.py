"""دستور pdev image — اطلاعات و تبدیل تصاویر."""
from __future__ import annotations

from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.table import Table

from persian_devkit.utils.image_utils import convert_image, image_info, resize_image

app = typer.Typer(help="اطلاعات و تبدیل تصاویر.", no_args_is_help=True)
console = Console()


def _human_size(n: int) -> str:
    """اندازهٔ خوانا برای بایت."""
    value = float(n)
    for unit in ("B", "KB", "MB", "GB"):
        if value < 1024:
            return f"{value:.1f} {unit}"
        value /= 1024
    return f"{value:.1f} TB"


@app.command("info")
def info_cmd(
    path: Path = typer.Argument(..., help="مسیر فایل تصویری."),
) -> None:
    """نمایش اطلاعات تصویر."""
    if not path.exists():
        console.print(f"[red]✗ خطا:[/red] فایل یافت نشد: {path}")
        raise typer.Exit(1)
    try:
        info = image_info(path)
    except Exception as e:
        console.print(f"[red]✗ خطا:[/red] {e}")
        raise typer.Exit(1)

    table = Table(title=f"🖼  {path.name}", title_style="bold cyan", show_header=False)
    table.add_column("شاخص", style="bold")
    table.add_column("مقدار")
    table.add_row("فرمت", info["format"])
    table.add_row("حالت رنگی", info["mode"])
    table.add_row("ابعاد", f"{info['width']} × {info['height']}")
    table.add_row("اندازه", _human_size(info["size_bytes"]))
    console.print(table)


@app.command("resize")
def resize_cmd(
    src: Path = typer.Argument(..., help="تصویر ورودی."),
    width: int = typer.Argument(..., help="عرض جدید."),
    height: Optional[int] = typer.Argument(None, help="ارتفاع جدید (اختیاری)."),
    output: Optional[Path] = typer.Option(None, "--output", "-o", help="مسیر خروجی."),
) -> None:
    """تغییر اندازهٔ تصویر (اگر ارتفاع ندهی، نسبت حفظ می‌شود)."""
    if not src.exists():
        console.print(f"[red]✗ خطا:[/red] فایل یافت نشد: {src}")
        raise typer.Exit(1)
    dst = output or src.with_stem(f"{src.stem}_resized")
    try:
        resize_image(src, dst, width, height)
    except Exception as e:
        console.print(f"[red]✗ خطا:[/red] {e}")
        raise typer.Exit(1)
    console.print(f"[green]✓ ذخیره شد:[/green] {dst}")


@app.command("convert")
def convert_cmd(
    src: Path = typer.Argument(..., help="تصویر ورودی."),
    output: Path = typer.Argument(..., help="مسیر خروجی (فرمت از پسوند)."),
    quality: int = typer.Option(
        90, "--quality", "-q", min=1, max=100, help="کیفیت JPEG."
    ),
) -> None:
    """تبدیل فرمت تصویر (مثلاً PNG → JPEG)."""
    if not src.exists():
        console.print(f"[red]✗ خطا:[/red] فایل یافت نشد: {src}")
        raise typer.Exit(1)
    try:
        convert_image(src, output, quality=quality)
    except Exception as e:
        console.print(f"[red]✗ خطا:[/red] {e}")
        raise typer.Exit(1)
    console.print(f"[green]✓ ذخیره شد:[/green] {output}")