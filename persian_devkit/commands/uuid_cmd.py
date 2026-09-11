"""دستور `pdev uuid` — تولید UUID."""
from __future__ import annotations

import base64
import uuid

import typer
from rich.console import Console

app = typer.Typer(help="تولید UUID.", no_args_is_help=True)
console = Console()


def short_uuid() -> str:
    """تولید UUID کوتاه بر پایهٔ Base64 (۲۲ کاراکتر)."""
    raw = uuid.uuid4().bytes
    return base64.urlsafe_b64encode(raw).rstrip(b"=").decode("ascii")


@app.command("new")
def new_cmd(
    count: int = typer.Option(
        1, "--count", "-c", min=1, max=10_000, help="تعداد UUID برای تولید."
    ),
    upper: bool = typer.Option(
        False, "--upper", "-u", help="خروجی با حروف بزرگ."
    ),
) -> None:
    """تولید UUID نسخهٔ ۴."""
    for _ in range(count):
        value = str(uuid.uuid4())
        if upper:
            value = value.upper()
        console.print(value)


@app.command("short")
def short_cmd(
    count: int = typer.Option(
        1, "--count", "-c", min=1, max=10_000, help="تعداد UUID کوتاه."
    ),
) -> None:
    """تولید UUID کوتاه (Base64، ۲۲ کاراکتر)."""
    for _ in range(count):
        console.print(short_uuid())