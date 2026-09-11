"""دستور pdev color — کار با رنگ‌ها (HEX, RGB, HSL)."""
from __future__ import annotations

import typer
from rich.console import Console
from rich.table import Table
from rich.text import Text

from persian_devkit.utils.color_utils import (
    best_text_color,
    complementary,
    contrast_ratio,
    generate_palette,
    parse_color,
    pleasant_color,
    random_color,
    rgb_to_hex,
    rgb_to_hsl,
)

app = typer.Typer(help="کار با رنگ‌ها (HEX, RGB, HSL).", no_args_is_help=True)
console = Console()


def _fail(message: str) -> None:
    console.print(f"[red]✗ خطا:[/red] {message}")
    raise typer.Exit(1)


def _swatch(rgb: tuple[int, int, int], text: str = "  ") -> Text:
    """نمایش یک بلوک رنگی در ترمینال."""
    r, g, b = rgb
    fg = best_text_color(rgb)
    return Text(text, style=f"{fg} on rgb({r},{g},{b})")


@app.command("convert")
def convert_cmd(
    color: str = typer.Argument(
        ..., help="رنگ: #fff، #ffffff، rgb(255,0,0) یا 255,0,0"
    ),
) -> None:
    """تبدیل رنگ بین فرمت‌های HEX، RGB و HSL."""
    try:
        rgb = parse_color(color)
    except ValueError as e:
        _fail(str(e))

    h, s, l = rgb_to_hsl(rgb)

    table = Table(title=f"🎨 {color}", title_style="bold cyan", show_header=False)
    table.add_column("فرمت", style="bold")
    table.add_column("مقدار")
    table.add_row("HEX", rgb_to_hex(rgb))
    table.add_row("RGB", f"rgb({rgb[0]}, {rgb[1]}, {rgb[2]})")
    table.add_row("HSL", f"hsl({h:.0f}, {s * 100:.0f}%, {l * 100:.0f}%)")
    table.add_row("روشنایی", f"{l * 100:.1f}%")
    table.add_row("نمایش", _swatch(rgb, "            "))
    console.print(table)


@app.command("palette")
def palette_cmd(
    color: str = typer.Argument(..., help="رنگ پایه."),
    count: int = typer.Option(5, "--count", "-c", min=2, max=12, help="تعداد."),
) -> None:
    """تولید پالت رنگی از یک رنگ پایه."""
    try:
        base = parse_color(color)
    except ValueError as e:
        _fail(str(e))

    palette = generate_palette(base, count=count)

    table = Table(title="🎨 پالت رنگ", title_style="bold cyan")
    table.add_column("نمونه", justify="center")
    table.add_column("HEX")
    table.add_column("RGB")

    for c in palette:
        table.add_row(
            _swatch(c, "        "),
            rgb_to_hex(c),
            f"{c[0]:3d}, {c[1]:3d}, {c[2]:3d}",
        )
    console.print(table)


@app.command("random")
def random_cmd(
    count: int = typer.Option(1, "--count", "-c", min=1, max=20, help="تعداد."),
    pleasant: bool = typer.Option(
        False, "--pleasant", "-p", help="رنگ‌های دلپذیر (اشباع کنترل‌شده)."
    ),
) -> None:
    """تولید رنگ تصادفی."""
    for _ in range(count):
        rgb = pleasant_color() if pleasant else random_color()
        console.print(f"{_swatch(rgb, '      ')}  {rgb_to_hex(rgb)}  rgb{rgb}")


@app.command("contrast")
def contrast_cmd(
    a: str = typer.Argument(..., help="رنگ اول."),
    b: str = typer.Argument(..., help="رنگ دوم."),
) -> None:
    """محاسبهٔ نسبت کنتراست بین دو رنگ (استاندارد WCAG)."""
    try:
        ca = parse_color(a)
        cb = parse_color(b)
    except ValueError as e:
        _fail(str(e))

    ratio = contrast_ratio(ca, cb)

    if ratio >= 7:
        level = "[green]AAA ✓[/green]"
    elif ratio >= 4.5:
        level = "[green]AA ✓[/green]"
    elif ratio >= 3:
        level = "[yellow]A (فقط متن بزرگ)[/yellow]"
    else:
        level = "[red]قابل قبول نیست[/red]"

    console.print(f"نسبت کنتراست: [bold]{ratio:.2f}:1[/bold]")
    console.print(f"سطح WCAG: {level}")


@app.command("complement")
def complement_cmd(
    color: str = typer.Argument(..., help="رنگ پایه."),
) -> None:
    """نمایش رنگ مکمل."""
    try:
        rgb = parse_color(color)
    except ValueError as e:
        _fail(str(e))

    comp = complementary(rgb)
    console.print(
        f"پایه: {_swatch(rgb, '      ')}  {rgb_to_hex(rgb)}\n"
        f"مکمل: {_swatch(comp, '      ')}  {rgb_to_hex(comp)}"
    )