"""دستور pdev template — رندر قالب ساده با متغیر."""
from __future__ import annotations

import re
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console

console = Console()

# سینتکس: {{var}} یا {{ var }}
_VAR_RE = re.compile(r"\{\{\s*([A-Za-z_][\w\.\-]*)\s*\}\}")


def render_template(text: str, variables: dict[str, str]) -> str:
    """جایگذاری متغیرها در قالب. متغیرهای تعریف‌نشده دست‌نخورده می‌مانند."""
    def replacer(m: re.Match) -> str:
        key = m.group(1)
        return variables.get(key, m.group(0))

    return _VAR_RE.sub(replacer, text)


def find_variables(text: str) -> list[str]:
    """لیست متغیرهای داخل قالب (بدون تکرار، به ترتیب ظهور)."""
    seen: list[str] = []
    for m in _VAR_RE.finditer(text):
        key = m.group(1)
        if key not in seen:
            seen.append(key)
    return seen


def template_command(
    file: Path = typer.Argument(..., help="مسیر فایل قالب."),
    var: list[str] = typer.Option(
        [], "--var", "-D", help="متغیر به شکل key=value (چند بار مجاز)."
    ),
    output: Optional[Path] = typer.Option(
        None, "--output", "-o", help="ذخیره در فایل خروجی."
    ),
    show_vars: bool = typer.Option(
        False, "--vars", "-V", help="فقط نمایش متغیرهای قالب (بدون رندر)."
    ),
) -> None:
    """رندر یک قالب متنی با متغیرها.

    مثال:
      pdev template greet.txt -D name=علی -D city=تهران
      pdev template config.tpl -D port=8080 -o config.yaml
      pdev template greet.txt --vars
    """
    if not file.exists():
        console.print(f"[red]✗ خطا:[/red] فایل یافت نشد: {file}")
        raise typer.Exit(1)

    text = file.read_text(encoding="utf-8")

    # حالت --vars: فقط نمایش متغیرها
    if show_vars:
        found = find_variables(text)
        if not found:
            console.print("[yellow]⚠ هیچ متغیری یافت نشد.[/yellow]")
            return
        console.print(f"متغیرهای یافت‌شده ({len(found)}):")
        for v in found:
            console.print(f"  • {v}")
        return

    # تجزیهٔ متغیرهای داده‌شده
    variables: dict[str, str] = {}
    for item in var:
        if "=" not in item:
            console.print(f"[red]✗ خطا:[/red] فرمت نامعتبر: {item} (باید key=value)")
            raise typer.Exit(1)
        k, v = item.split("=", 1)
        variables[k.strip()] = v

    rendered = render_template(text, variables)

    if output:
        output.write_text(rendered, encoding="utf-8")
        console.print(f"[green]✓ ذخیره شد:[/green] {output}")
    else:
        console.print(rendered, highlight=False, markup=False)