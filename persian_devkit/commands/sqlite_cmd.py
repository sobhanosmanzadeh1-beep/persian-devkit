"""دستور pdev sqlite — کار با دیتابیس SQLite."""
from __future__ import annotations

from pathlib import Path

import typer
from rich.console import Console
from rich.table import Table

from persian_devkit.utils.db_utils import (
    execute_query,
    export_table_to_csv,
    get_schema,
    list_tables,
    open_db,
    table_count,
)

app = typer.Typer(help="کار با دیتابیس SQLite.", no_args_is_help=True)
console = Console()


def _fail(msg: str) -> None:
    console.print(f"[red]✗ خطا:[/red] {msg}")
    raise typer.Exit(1)


def _open(path: Path):
    if not path.exists():
        _fail(f"فایل یافت نشد: {path}")
    try:
        return open_db(path)
    except Exception as e:
        _fail(f"خطا در باز کردن دیتابیس: {e}")


@app.command("tables")
def tables_cmd(
    db: Path = typer.Argument(..., help="مسیر فایل SQLite."),
) -> None:
    """لیست جدول‌های دیتابیس."""
    with _open(db) as conn:
        tables = list_tables(conn)
        if not tables:
            console.print("[yellow]⚠ جدولی یافت نشد.[/yellow]")
            return
        table = Table(title=f" جدول‌های {db.name}", title_style="bold cyan")
        table.add_column("نام جدول", style="bold")
        table.add_column("تعداد ردیف", justify="right", style="green")
        for t in tables:
            try:
                count = table_count(conn, t)
            except ValueError:
                count = -1
            table.add_row(t, str(count) if count >= 0 else "?")
        console.print(table)


@app.command("schema")
def schema_cmd(
    db: Path = typer.Argument(..., help="مسیر فایل SQLite."),
    table_name: str = typer.Option(None, "--table", "-t", help="نام جدول خاص."),
) -> None:
    """نمایش ساختار جدول(ها)."""
    with _open(db) as conn:
        try:
            schemas = get_schema(conn, table_name)
        except Exception as e:
            _fail(str(e))

        if not schemas:
            console.print("[yellow]⚠ جدولی یافت نشد.[/yellow]")
            return

        for s in schemas:
            t = Table(title=f"🔍 {s['table']}", title_style="bold cyan")
            t.add_column("ستون", style="bold")
            t.add_column("نوع")
            t.add_column("PK", justify="center")
            t.add_column("NOT NULL", justify="center")
            t.add_column("Default")
            for c in s["columns"]:
                t.add_row(
                    c["name"],
                    c["type"],
                    "✓" if c["primary_key"] else "",
                    "✓" if c["notnull"] else "",
                    str(c["default"]) if c["default"] is not None else "",
                )
            console.print(t)


@app.command("query")
def query_cmd(
    db: Path = typer.Argument(..., help="مسیر فایل SQLite."),
    sql: str = typer.Argument(..., help="کوئری SQL."),
    limit: int = typer.Option(50, "--limit", "-n", min=1, max=1000),
) -> None:
    """اجرای کوئری SELECT (نمایش جدولی)."""
    with _open(db) as conn:
        try:
            result = execute_query(conn, sql)
        except ValueError as e:
            _fail(str(e))

        if result["type"] == "select":
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
        else:
            console.print(
                f"[green]✓[/green] {result['affected']} ردیف تغییر یافت."
            )


@app.command("exec")
def exec_cmd(
    db: Path = typer.Argument(..., help="مسیر فایل SQLite."),
    sql: str = typer.Argument(..., help="SQL برای اجرا (INSERT/UPDATE/DELETE)."),
) -> None:
    """اجرای کوئری نوشتنی (INSERT/UPDATE/DELETE/CREATE)."""
    with _open(db) as conn:
        try:
            result = execute_query(conn, sql)
        except ValueError as e:
            _fail(str(e))

        if result["type"] == "write":
            console.print(
                f"[green]✓[/green] {result['affected']} ردیف تغییر یافت."
            )
        else:
            console.print("[yellow]⚠ این دستور برای SELECT است؛ از `query` استفاده کن.[/yellow]")


@app.command("export")
def export_cmd(
    db: Path = typer.Argument(..., help="مسیر فایل SQLite."),
    table_name: str = typer.Argument(..., help="نام جدول."),
    output: Path = typer.Argument(..., help="مسیر فایل CSV خروجی."),
) -> None:
    """خروجی CSV از یک جدول."""
    with _open(db) as conn:
        try:
            count = export_table_to_csv(conn, table_name, output)
        except ValueError as e:
            _fail(str(e))
        console.print(f"[green]✓[/green] {count} ردیف ذخیره شد در {output}")