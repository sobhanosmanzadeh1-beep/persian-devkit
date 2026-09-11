"""دستور pdev base64 — رمزگذاری و رمزگشایی Base64."""
from __future__ import annotations

import sys
from typing import Optional

import typer
from rich.console import Console

from persian_devkit.utils.crypto_utils import b64_decode, b64_encode

app = typer.Typer(help="رمزگذاری و رمزگشایی Base64.", no_args_is_help=True)
console = Console()


def _read(value: Optional[str]) -> str:
    """متن را از آرگومان یا stdin می‌خواند."""
    if value is not None and value != "":
        return value
    if not sys.stdin.isatty():
        data = sys.stdin.read()
        if data.strip():
            return data.rstrip("\n")
    console.print("[red]✗ خطا:[/red] متنی وارد نشده.")
    raise typer.Exit(1)


@app.command("encode")
def encode_cmd(
    text: Optional[str] = typer.Argument(None, help="متن ورودی (یا از stdin)."),
    url_safe: bool = typer.Option(
        False, "--url-safe", "-u", help="استفاده از الفبای URL-safe."
    ),
) -> None:
    """رمزگذاری متن به Base64."""
    console.print(b64_encode(_read(text), url_safe=url_safe))


@app.command("decode")
def decode_cmd(
    text: Optional[str] = typer.Argument(None, help="رشتهٔ Base64 (یا از stdin)."),
    url_safe: bool = typer.Option(
        False, "--url-safe", "-u", help="ورودی با الفبای URL-safe."
    ),
) -> None:
    """رمزگشایی Base64 به متن."""
    try:
        console.print(b64_decode(_read(text), url_safe=url_safe))
    except ValueError as e:
        console.print(f"[red]✗ خطا:[/red] {e}")
        raise typer.Exit(1)