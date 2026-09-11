"""دستور pdev password — تولید و سنجش رمز عبور."""
from __future__ import annotations

import typer
from rich.console import Console
from rich.table import Table

from persian_devkit.utils.crypto_utils import (
    generate_password,
    password_strength,
)

app = typer.Typer(help="تولید و سنجش رمز عبور.", no_args_is_help=True)
console = Console()


@app.command("new")
def new_cmd(
    length: int = typer.Option(16, "--length", "-l", min=4, max=256, help="طول رمز."),
    no_symbols: bool = typer.Option(False, "--no-symbols", help="بدون نمادها."),
    no_upper: bool = typer.Option(False, "--no-upper", help="بدون حروف بزرگ."),
    no_digits: bool = typer.Option(False, "--no-digits", help="بدون ارقام."),
    count: int = typer.Option(1, "--count", "-c", min=1, max=100, help="تعداد."),
) -> None:
    """تولید رمز عبور امن."""
    try:
        for _ in range(count):
            console.print(
                generate_password(
                    length=length,
                    use_upper=not no_upper,
                    use_digits=not no_digits,
                    use_symbols=not no_symbols,
                )
            )
    except ValueError as e:
        console.print(f"[red]✗ خطا:[/red] {e}")
        raise typer.Exit(1)


@app.command("check")
def check_cmd(
    password: str = typer.Argument(..., help="رمز برای سنجش قدرت."),
) -> None:
    """سنجش قدرت رمز عبور."""
    result = password_strength(password)

    color = "red" if result["score"] < 40 else "yellow" if result["score"] < 70 else "green"
    table = Table(title=" قدرت رمز", title_style="bold cyan")
    table.add_column("شاخص", style="bold")
    table.add_column("مقدار")
    table.add_row("امتیاز", f"[{color}]{result['score']}/100[/{color}]")
    table.add_row("برچسب", f"[{color}]{result['label']}[/{color}]")
    table.add_row("آنتروپی", f"{result['entropy']} بیت")
    console.print(table)