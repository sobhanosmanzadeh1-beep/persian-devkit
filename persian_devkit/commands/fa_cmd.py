"""دستور pdev fa — ابزارهای پیشرفتهٔ فارسی."""
from __future__ import annotations

import sys
from typing import Optional

import typer
from rich.console import Console
from rich.table import Table

from persian_devkit.utils.persian_utils import (
    add_kashida,
    char_info,
    fix_prefixes,
    fix_spacing,
    fix_suffixes,
    has_hamza,
    is_persian_char,
    justify_line,
    normalize_hamza,
    remove_kashida,
    text_to_visual,
)

app = typer.Typer(help="ابزارهای پیشرفتهٔ فارسی (همزه، کشیده، پیشوند).", no_args_is_help=True)
console = Console()


def _read(text: Optional[str]) -> str:
    if text is not None and text != "":
        return text
    if not sys.stdin.isatty():
        data = sys.stdin.read()
        if data.strip():
            return data.rstrip("\n")
    console.print("[red]✗ خطا:[/red] متنی وارد نشده.")
    raise typer.Exit(1)


#همزه


@app.command("hamza")
def hamza_cmd(
    text: Optional[str] = typer.Argument(None, help="متن (یا از stdin)."),
    keep_aa: bool = typer.Option(
        True, "--keep-aa/--no-keep-aa", help="حفظ «آ» به‌عنوان یک کاراکتر خاص."
    ),
) -> None:
    """یکسان‌سازی انواع همزه.

    «أحمد» → «احمد»، «مؤمن» → «مومن»، «مسئله» → «مسئله»
    """
    console.print(normalize_hamza(_read(text), keep_aa=keep_aa))


#کشیده


@app.command("kashida")
def kashida_cmd(
    text: Optional[str] = typer.Argument(None, help="متن (یا از stdin)."),
    width: int = typer.Option(0, "--width", "-w", min=0, help="طول هدف (۰ = فقط افزودن یک کشیده)."),
    remove: bool = typer.Option(False, "--remove", "-r", help="حذف همهٔ کشیده‌ها."),
) -> None:
    """افزودن یا حذف کشیده (تطویل)."""
    content = _read(text)

    if remove:
        console.print(remove_kashida(content))
        return

    if width > 0:
        console.print(justify_line(content, width))
    else:
        # به هر کلمه یک کشیده اضافه کن
        words = content.split()
        result = " ".join(add_kashida(w, len(w) + 1) for w in words)
        console.print(result)


#پیشوند/پسوند


@app.command("pish")
def pish_cmd(
    text: Optional[str] = typer.Argument(None, help="متن (یا از stdin)."),
) -> None:
    """اصلاح پیشوندهای چسبیده (می، نمی، بی).

    «میروم» → «می‌روم»
    «نمیدانم» → «نمی‌دانم»
    """
    console.print(fix_prefixes(_read(text)))


@app.command("suffix")
def suffix_cmd(
    text: Optional[str] = typer.Argument(None, help="متن (یا از stdin)."),
) -> None:
    """اصلاح پسوندهای چسبیده (ها، تر، ترین).

    «کتابها» → «کتاب‌ها»
    «بهتری» → «بهتری»
    """
    console.print(fix_suffixes(_read(text)))


@app.command("fix")
def fix_cmd(
    text: Optional[str] = typer.Argument(None, help="متن (یا از stdin)."),
) -> None:
    """اصلاح همهٔ پیشوندها و پسوندها."""
    console.print(fix_spacing(_read(text)))


#charinfo


@app.command("charinfo")
def charinfo_cmd(
    char: str = typer.Argument(..., help="یک کاراکتر برای تحلیل."),
) -> None:
    """اطلاعات یونیکد یک کاراکتر."""
    if len(char) != 1:
        console.print("[red]✗ خطا:[/red] فقط یک کاراکتر وارد کن.")
        raise typer.Exit(1)

    info = char_info(char)

    table = Table(title=f" U+{ord(char):04X}", title_style="bold cyan", show_header=False)
    table.add_column("شاخص", style="bold")
    table.add_column("مقدار", style="green")
    table.add_row("کاراکتر", info["char"])
    table.add_row("Code Point", info["code_point"])
    table.add_row("Decimal", str(info["decimal"]))
    table.add_row("Hex", info["hex"])
    table.add_row("Name", info["name"])
    table.add_row("Category", info["category"])
    table.add_row("حرف؟", "✓" if info["is_letter"] else "✗")
    table.add_row("رقم؟", "✓" if info["is_digit"] else "✗")
    table.add_row("فارسی؟", "✓" if info["is_persian"] else "✗")
    table.add_row("نیم‌فاصله؟", "✓" if info["is_zwnj"] else "✗")
    table.add_row("کشیده؟", "✓" if info["is_kashida"] else "✗")
    console.print(table)


@app.command("charmap")
def charmap_cmd(
    text: Optional[str] = typer.Argument(None, help="متن برای تحلیل."),
) -> None:
    """جدول اطلاعات یونیکد برای هر کاراکتر متن."""
    content = _read(text)

    table = Table(title=" نقشهٔ کاراکترها", title_style="bold cyan")
    table.add_column("#", style="dim")
    table.add_column("کاراکتر", justify="center")
    table.add_column("Code Point")
    table.add_column("فارسی؟", justify="center")
    table.add_column("Name")

    for i, ch in enumerate(content[:100], 1):
        info = char_info(ch)
        table.add_row(
            str(i),
            ch if ch.strip() else "␣",
            info["code_point"],
            "✓" if info["is_persian"] else "",
            info["name"][:40],
        )
    console.print(table)

    if len(content) > 100:
        console.print(f"[dim]... و {len(content) - 100} کاراکتر دیگر[/dim]")


#bidi


@app.command("bidi")
def bidi_cmd(
    text: Optional[str] = typer.Argument(None, help="متن (یا از stdin)."),
    base_dir: str = typer.Option("R", "--base", "-b", help="جهت پایه: R یا L."),
) -> None:
    """تبدیل متن به ترتیب بصری برای نمایش در ترمینال‌های LTR.

    مفید وقتی متن فارسی روی ترمینال‌های ساده درست نمایش داده نمی‌شود.
    """
    if base_dir not in ("R", "L"):
        console.print("[red]✗ خطا:[/red] base باید R یا L باشد.")
        raise typer.Exit(1)

    try:
        result = text_to_visual(_read(text), base_dir=base_dir)
    except RuntimeError as e:
        console.print(f"[red]✗ خطا:[/red] {e}")
        raise typer.Exit(1)

    console.print(result)


#alphabet


@app.command("alphabet")
def alphabet_cmd() -> None:
    """نمایش الفبای فارسی با اطلاعات."""
    letters = "آابپتثجچحخدذرزژسشصضطظعغفقکگلمنوهی"
    for ch in letters:
        info = char_info(ch)
        console.print(f"[bold]{ch}[/bold]  {info['code_point']}  {info['name']}")