"""دستور pdev qrcode — تولید QR Code از متن."""
from __future__ import annotations

from pathlib import Path
from typing import Optional

import typer
from rich.console import Console

from persian_devkit.utils.qrcode_utils import qr_to_ascii, qr_to_image

console = Console()


def qrcode_command(
    text: str = typer.Argument(..., help="متن یا URL برای رمزگذاری."),
    output: Optional[Path] = typer.Option(
        None, "--output", "-o", help="ذخیره به فایل تصویری (پسوند از نام)."
    ),
    error: str = typer.Option(
        "M", "--error", "-e", help="سطح تصحیح خطا: L, M, Q, H."
    ),
    box_size: int = typer.Option(
        10, "--box-size", "-b", min=1, max=50, help="اندازهٔ هر بلوک (فقط برای فایل)."
    ),
    border: int = typer.Option(
        2, "--border", min=0, max=10, help="حاشیه (فقط برای فایل)."
    ),
) -> None:
    """تولید QR Code از متن (فارسی یا انگلیسی)."""
    if output is not None:
        try:
            qr_to_image(text, output, error=error, box_size=box_size, border=border)
        except Exception as e:
            console.print(f"[red]✗ خطا:[/red] {e}")
            raise typer.Exit(1)
        console.print(f"[green]✓ ذخیره شد:[/green] {output}")
        return

    try:
        art = qr_to_ascii(text, error=error, border=1)
    except Exception as e:
        console.print(f"[red]✗ خطا:[/red] {e}")
        raise typer.Exit(1)

    console.print(art, highlight=False, markup=False, soft_wrap=True)