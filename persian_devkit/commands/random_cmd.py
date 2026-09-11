"""دستور pdev random — تولید مقادیر تصادفی."""
from __future__ import annotations

import secrets
import string

import typer
from rich.console import Console

from persian_devkit.utils.crypto_utils import nanoid

app = typer.Typer(help="تولید مقادیر تصادفی.", no_args_is_help=True)
console = Console()


@app.command("int")
def int_cmd(
    low: int = typer.Argument(0, help="کران پایین (شامل)."),
    high: int = typer.Argument(100, help="کران بالا (شامل)."),
    count: int = typer.Option(1, "--count", "-c", min=1, help="تعداد."),
) -> None:
    """تولید عدد صحیح تصادفی در بازه."""
    if low > high:
        console.print("[red]✗ خطا:[/red] کران پایین بزرگ‌تر از بالا است.")
        raise typer.Exit(1)
    for _ in range(count):
        console.print(secrets.randbelow(high - low + 1) + low)


@app.command("str")
def str_cmd(
    length: int = typer.Option(16, "--length", "-l", min=1, help="طول."),
    count: int = typer.Option(1, "--count", "-c", min=1, help="تعداد."),
    alphabet: str = typer.Option(
        "full",
        "--alphabet",
        "-a",
        help="مجموعهٔ کاراکتر: letters, digits, hex, full.",
    ),
) -> None:
    """تولید رشتهٔ تصادفی."""
    pools = {
        "letters": string.ascii_letters,
        "digits": string.digits,
        "hex": "0123456789abcdef",
        "full": string.ascii_letters + string.digits,
    }
    if alphabet not in pools:
        console.print(f"[red]✗ خطا:[/red] مجموعهٔ ناشناخته: {alphabet}")
        raise typer.Exit(1)
    pool = pools[alphabet]
    for _ in range(count):
        console.print("".join(secrets.choice(pool) for _ in range(length)))


@app.command("choice")
def choice_cmd(
    items: list[str] = typer.Argument(..., help="گزینه‌ها برای انتخاب."),
    count: int = typer.Option(1, "--count", "-c", min=1, help="تعداد انتخاب."),
    replace: bool = typer.Option(
        False, "--replace", "-r", help="انتخاب با جای‌گذاری (تکرار مجاز)."
    ),
) -> None:
    """انتخاب تصادفی از میان گزینه‌ها."""
    if count > len(items) and not replace:
        console.print(
            "[red]✗ خطا:[/red] تعداد بیشتر از گزینه‌هاست. از --replace استفاده کن."
        )
        raise typer.Exit(1)
    if replace:
        for _ in range(count):
            console.print(secrets.choice(items))
    else:
        # Fisher-Yates با secrets
        pool = list(items)
        for i in range(count):
            j = i + secrets.randbelow(len(pool) - i)
            pool[i], pool[j] = pool[j], pool[i]
            console.print(pool[i])


@app.command("coin")
def coin_cmd(
    count: int = typer.Option(1, "--count", "-c", min=1, help="تعداد پرتاب."),
    heads_label: str = typer.Option("شیر", "--heads"),
    tails_label: str = typer.Option("خط", "--tails"),
) -> None:
    """پرتاب سکه."""
    for _ in range(count):
        console.print(heads_label if secrets.randbelow(2) == 0 else tails_label)


@app.command("dice")
def dice_cmd(
    sides: int = typer.Option(6, "--sides", "-s", min=2, help="تعداد وجه."),
    count: int = typer.Option(1, "--count", "-c", min=1, help="تعداد تاس."),
) -> None:
    """پرتاب تاس."""
    for _ in range(count):
        console.print(secrets.randbelow(sides) + 1)


@app.command("nanoid")
def nanoid_cmd(
    length: int = typer.Option(21, "--length", "-l", min=1, help="طول."),
    count: int = typer.Option(1, "--count", "-c", min=1, help="تعداد."),
) -> None:
    """تولید Nano ID."""
    for _ in range(count):
        console.print(nanoid(length))