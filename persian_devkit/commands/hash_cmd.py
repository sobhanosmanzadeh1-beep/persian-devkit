"""دستور pdev hash — محاسبهٔ هش متن یا فایل."""
from __future__ import annotations

import sys
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.table import Table

from persian_devkit.utils.crypto_utils import HASH_ALGOS, hash_file, hash_text

app = typer.Typer(help="محاسبهٔ هش متن یا فایل.", no_args_is_help=True)
console = Console()


def _read(value: Optional[str]) -> str:
    if value is not None and value != "":
        return value
    if not sys.stdin.isatty():
        data = sys.stdin.read()
        if data.strip():
            return data.rstrip("\n")
    console.print("[red]✗ خطا:[/red] متنی وارد نشده.")
    raise typer.Exit(1)


@app.command("text")
def text_cmd(
    text: Optional[str] = typer.Argument(None, help="متن ورودی (یا از stdin)."),
    algo: str = typer.Option(
        "sha256", "--algo", "-a", help=f"الگوریتم: {'/'.join(HASH_ALGOS)}"
    ),
) -> None:
    """محاسبهٔ هش یک متن."""
    if algo not in HASH_ALGOS:
        console.print(f"[red]✗ خطا:[/red] الگوریتم ناشناخته: {algo}")
        raise typer.Exit(1)
    console.print(hash_text(_read(text), algo=algo))


@app.command("file")
def file_cmd(
    path: Path = typer.Argument(..., help="مسیر فایل."),
    algo: str = typer.Option(
        "sha256", "--algo", "-a", help=f"الگوریتم: {'/'.join(HASH_ALGOS)}"
    ),
) -> None:
    """محاسبهٔ هش یک فایل."""
    if not path.exists():
        console.print(f"[red]✗ خطا:[/red] فایل یافت نشد: {path}")
        raise typer.Exit(1)
    if algo not in HASH_ALGOS:
        console.print(f"[red]✗ خطا:[/red] الگوریتم ناشناخته: {algo}")
        raise typer.Exit(1)
    console.print(hash_file(path, algo=algo))


@app.command("all")
def all_cmd(
    text: Optional[str] = typer.Argument(None, help="متن ورودی (یا از stdin)."),
) -> None:
    """محاسبهٔ همهٔ الگوریتم‌ها روی یک متن."""
    value = _read(text)
    table = Table(title=" هش‌ها", title_style="bold cyan")
    table.add_column("الگوریتم", style="bold")
    table.add_column("مقدار", overflow="fold")
    for algo in HASH_ALGOS:
        table.add_row(algo, hash_text(value, algo=algo))
    console.print(table)