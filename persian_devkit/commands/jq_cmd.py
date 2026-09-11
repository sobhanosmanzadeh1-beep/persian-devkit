"""دستور pdev jq — کوئری JSON با JSONPath ساده."""
from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.syntax import Syntax

from persian_devkit.utils.jsonpath_utils import JSONPathError, query

console = Console()


def jq_command(
    path: str = typer.Argument(
        ..., help="مسیر JSONPath (مثل .user.name یا .items[0])."
    ),
    file: Optional[Path] = typer.Option(
        None, "--file", "-f", help="فایل JSON ورودی (یا از stdin)."
    ),
    raw: bool = typer.Option(
        False, "--raw", "-r", help="خروجی خام (بدون رنگ و بدون JSON encoding)."
    ),
    compact: bool = typer.Option(False, "--compact", "-c", help="خروجی فشرده."),
) -> None:
    """کوئری روی JSON با JSONPath.

    مسیرها:
      .key                → دسترسی به کلید
      .a.b.c              → تودرتو
      .items[0]           → اندیس آرایه
      .items[*].name      → همهٔ نام‌ها
      ["key with space"]  → کلید با فاصله
    """
    # خواندن داده
    if file is not None:
        if not file.exists():
            console.print(f"[red]✗ خطا:[/red] فایل یافت نشد: {file}")
            raise typer.Exit(1)
        text = file.read_text(encoding="utf-8")
    else:
        if sys.stdin.isatty():
            console.print(
                "[red]✗ خطا:[/red] فایل JSON بده یا از stdin استفاده کن."
            )
            raise typer.Exit(1)
        text = sys.stdin.read()

    try:
        data = json.loads(text)
    except json.JSONDecodeError as e:
        console.print(f"[red]✗ خطا:[/red] JSON نامعتبر: {e}")
        raise typer.Exit(1)

    try:
        result = query(data, path)
    except JSONPathError as e:
        console.print(f"[red]✗ خطا:[/red] {e}")
        raise typer.Exit(1)

    # خروجی
    if raw:
        if isinstance(result, str):
            console.print(result, highlight=False)
        elif isinstance(result, (int, float, bool)) or result is None:
            console.print(str(result), highlight=False)
        else:
            console.print(
                json.dumps(result, ensure_ascii=False), highlight=False
            )
        return

    if compact:
        console.print(
            json.dumps(result, ensure_ascii=False, separators=(",", ":")),
            highlight=False,
        )
        return

    if isinstance(result, str):
        console.print(result)
    elif isinstance(result, (int, float, bool)) or result is None:
        console.print(str(result))
    else:
        text_out = json.dumps(result, ensure_ascii=False, indent=2)
        console.print(
            Syntax(text_out, "json", word_wrap=True, background_color="default")
        )