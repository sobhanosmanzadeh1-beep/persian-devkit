"""دستور pdev http — ارسال درخواست HTTP."""
from __future__ import annotations

import json

import typer
from rich.console import Console
from rich.table import Table

from persian_devkit.utils.http_utils import http_request

app = typer.Typer(help="ارسال درخواست HTTP.", no_args_is_help=True)
console = Console()


def _status_style(code: int) -> str:
    """رنگ بر اساس کد وضعیت."""
    if 200 <= code < 300:
        return "green"
    if 300 <= code < 400:
        return "cyan"
    if 400 <= code < 500:
        return "yellow"
    return "red"


@app.command("get")
def get_cmd(
    url: str = typer.Argument(..., help="آدرس URL."),
    show_headers: bool = typer.Option(
        False, "--headers", "-H", help="نمایش هدرها."
    ),
    timeout: float = typer.Option(10.0, "--timeout", "-t", min=1.0, max=60.0),
) -> None:
    """ارسال درخواست GET."""
    _do_request("GET", url, show_headers, timeout)


@app.command("head")
def head_cmd(
    url: str = typer.Argument(..., help="آدرس URL."),
    show_headers: bool = typer.Option(True, "--headers/--no-headers"),
    timeout: float = typer.Option(10.0, "--timeout", "-t"),
) -> None:
    """ارسال درخواست HEAD (فقط هدرها)."""
    _do_request("HEAD", url, show_headers, timeout)


@app.command("post")
def post_cmd(
    url: str = typer.Argument(..., help="آدرس URL."),
    data: str = typer.Option("{}", "--data", "-d", help="دادهٔ JSON."),
    timeout: float = typer.Option(10.0, "--timeout", "-t"),
) -> None:
    """ارسال درخواست POST با JSON."""
    try:
        json.loads(data)
    except json.JSONDecodeError as e:
        console.print(f"[red]✗ خطا:[/red] JSON نامعتبر: {e}")
        raise typer.Exit(1)
    _do_request("POST", url, True, timeout, data=data)


def _do_request(
    method: str,
    url: str,
    show_headers: bool,
    timeout: float,
    data: str | None = None,
) -> None:
    """انجام درخواست و نمایش نتیجه."""
    try:
        result = http_request(url, method=method, timeout=timeout)
    except ValueError as e:
        console.print(f"[red]✗ خطا:[/red] {e}")
        raise typer.Exit(1)

    style = _status_style(result["status"])
    console.print(
        f"[{style}]{result['status']} {result['reason']}[/{style}]  "
        f"[dim]({result['elapsed_ms']} ms, "
        f"{result['content_length']} bytes)[/dim]"
    )

    if result["redirected"]:
        console.print(f"[cyan]→ redirected to:[/cyan] {result['url']}")

    if show_headers:
        table = Table(title=" Headers", title_style="bold cyan", show_header=False)
        table.add_column("Header", style="bold")
        table.add_column("Value")
        for k, v in result["headers"].items():
            table.add_row(k, v)
        console.print(table)

    if result["text_preview"]:
        console.print("\n[dim]─── محتوا (پیش‌نمایش) ───[/dim]")
        console.print(result["text_preview"], highlight=False)