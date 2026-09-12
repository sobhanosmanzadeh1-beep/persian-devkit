"""دستور pdev csv-query — کوئری SQL روی فایل CSV."""
from __future__ import annotations

from pathlib import Path

import typer
from rich.console import Console
from rich.table import Table

from persian_devkit.utils.db_utils import execute_query, load_csv_to_memory

app = typer.Typer(help="کوئری SQL روی فایل CSV.", no_args_is_help=True)
console = Console()


@app.command("query")
def query_cmd(
    path: Path = typer.Argument(..., help="مسیر فایل CSV."),
    sql: str = typer.Argument(
        ..., help="کوئری SQL (جدول با نام data)."
    ),
    limit: int = typer.Option(50, "--limit", "-n", min=1, max=1000),
) -> None:
    """اجرای کوئری SQL روی CSV (جدول با نام `data`).

    مثال:
      pdev csv-query query data.csv "SELECT * FROM data WHERE age > 30"
      pdev csv-query query data.csv "SELECT city, COUNT(*) FROM data GROUP BY city"
    """
    if not path.exists():
        console.print(f"[red]✗ خطا:[/red] فایل یافت نشد: {path}")
        raise typer.Exit(1)

    try:
        conn, _ = load_csv_to_memory(path)
    except ValueError as e:
        console.print(f"[red]✗ خطا:[/red] {e}")
        raise typer.Exit(1)

    try:
        result = execute_query(conn, sql)
    except ValueError as e:
        console.print(f"[red]✗ خطا:[/red] {e}")
        raise typer.Exit(1)
    finally:
        conn.close()

    if result["type"] != "select":
        console.print("[yellow]⚠ این دستور فقط SELECT را پشتیبانی می‌کند.[/yellow]")
        raise typer.Exit(1)

    if not result["rows"]:
        console.print("[yellow]⚠ نتیجه‌ای یافت نشد.[/yellow]")
        return

    table = Table(title=f" {result['count']} ردیف", title_style="bold cyan")
    for col in result["columns"]:
        table.add_column(str(col))
    for row in result["rows"][:limit]:
        table.add_row(*[str(v) if v is not None else "NULL" for v in row])
    console.print(table)
    if result["count"] > limit:
        console.print(f"[dim]... و {result['count'] - limit} ردیف دیگر[/dim]")


@app.command("columns")
def columns_cmd(
    path: Path = typer.Argument(..., help="مسیر فایل CSV."),
) -> None:
    """نمایش نام ستون‌های CSV."""
    if not path.exists():
        console.print(f"[red]✗ خطا:[/red] فایل یافت نشد: {path}")
        raise typer.Exit(1)

    try:
        conn, _ = load_csv_to_memory(path)
    except ValueError as e:
        console.print(f"[red]✗ خطا:[/red] {e}")
        raise typer.Exit(1)

    try:
        cur = conn.cursor()
        cur.execute("PRAGMA table_info(data)")
        for row in cur.fetchall():
            console.print(f"  • {row[1]} ({row[2]})")
    finally:
        conn.close()