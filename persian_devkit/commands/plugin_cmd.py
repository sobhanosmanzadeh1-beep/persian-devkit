"""دستور pdev plugin — مدیریت پلاگین‌ها."""
from __future__ import annotations

import typer
from rich.console import Console
from rich.table import Table

from persian_devkit.utils import plugin_utils

app = typer.Typer(help="مدیریت پلاگین‌ها.", no_args_is_help=True)
console = Console()

_EXAMPLE_PLUGIN = '''"""پلاگین نمونه: دستور pdev hello."""
import typer
from rich.console import Console

app = typer.Typer(help="پلاگین نمونه.")
console = Console()


@app.command("world")
def world() -> None:
    """چاپ سلام."""
    console.print("[green]سلام از پلاگین![/green]")
'''


@app.command("list")
def list_cmd() -> None:
    """لیست پلاگین‌های نصب‌شده."""
    plugins = plugin_utils.discover_plugins()
    if not plugins:
        console.print("[yellow]هیچ پلاگینی نصب نیست.[/yellow]")
        console.print(f"مسیر: [dim]{plugin_utils.PLUGINS_DIR}[/dim]")
        console.print("[dim]برای ساخت نمونه: pdev plugin init[/dim]")
        return

    table = Table(title="🔌 پلاگین‌ها", title_style="bold cyan")
    table.add_column("نام", style="bold")
    table.add_column("توضیح")
    table.add_column("مسیر", style="dim")
    for p in plugins:
        table.add_row(p.name, p.description or "—", str(p.path))
    console.print(table)


@app.command("path")
def path_cmd() -> None:
    """مسیر پوشهٔ پلاگین‌ها."""
    console.print(str(plugin_utils.PLUGINS_DIR))


@app.command("init")
def init_cmd() -> None:
    """ساخت پوشهٔ پلاگین‌ها + یک نمونهٔ آماده."""
    plugin_utils.ensure_plugins_dir()
    example = plugin_utils.PLUGINS_DIR / "hello.py"
    if not example.exists():
        example.write_text(_EXAMPLE_PLUGIN, encoding="utf-8")
        console.print(f"[green]✓[/green] پلاگین نمونه ساخته شد: {example}")
    else:
        console.print(f"[yellow]فایل نمونه از قبل موجود است:[/yellow] {example}")
    console.print("[dim]برای تست: pdev hello world[/dim]")


@app.command("validate")
def validate_cmd(
    name: str = typer.Argument(..., help="نام پلاگین (بدون .py)."),
) -> None:
    """بررسی سلامت یک پلاگین."""
    path = plugin_utils.PLUGINS_DIR / f"{name}.py"
    if not path.exists():
        console.print(f"[red]✗ یافت نشد:[/red] {path}")
        raise typer.Exit(1)

    try:
        plugin_app = plugin_utils.load_plugin(path)
    except ValueError as e:
        console.print(f"[red]✗ خطا:[/red] {e}")
        raise typer.Exit(1)

    if plugin_app is None:
        console.print(
            "[red]✗ پلاگین باید متغیر `app` از نوع `typer.Typer` داشته باشد.[/red]"
        )
        raise typer.Exit(1)

    console.print(f"[green]✓[/green] پلاگین [bold]{name}[/bold] سالم است.")


@app.command("remove")
def remove_cmd(
    name: str = typer.Argument(..., help="نام پلاگین."),
    force: bool = typer.Option(False, "--force", "-f", help="بدون تأیید."),
) -> None:
    """حذف یک پلاگین."""
    path = plugin_utils.PLUGINS_DIR / f"{name}.py"
    if not path.exists():
        console.print(f"[red]✗ یافت نشد:[/red] {path}")
        raise typer.Exit(1)

    if not force:
        confirm = typer.confirm(f"حذف پلاگین {name}؟")
        if not confirm:
            console.print("[dim]لغو شد.[/dim]")
            return

    path.unlink()
    console.print(f"[green]✓[/green] حذف شد: {name}")