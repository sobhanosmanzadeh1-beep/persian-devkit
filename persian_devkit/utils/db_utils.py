"""توابع کمکی کار با SQLite و کوئری CSV."""
from __future__ import annotations

import csv
import io
import sqlite3
from pathlib import Path
from typing import Any, Optional, Union


def open_db(path: Path) -> sqlite3.Connection:
    """اتصال به فایل SQLite (اگر نباشد، می‌سازد)."""
    return sqlite3.connect(str(path))


def list_tables(conn: sqlite3.Connection) -> list[str]:
    """لیست جدول‌های دیتابیس."""
    cur = conn.cursor()
    cur.execute(
        "SELECT name FROM sqlite_master "
        "WHERE type='table' AND name NOT LIKE 'sqlite_%' "
        "ORDER BY name"
    )
    return [row[0] for row in cur.fetchall()]


def get_schema(conn: sqlite3.Connection, table: Optional[str] = None) -> list[dict]:
    """ساختار جدول(ها): نام، نوع ستون، NOT NULL، default."""
    cur = conn.cursor()
    tables = [table] if table else list_tables(conn)
    result: list[dict] = []
    for tbl in tables:
        cur.execute(f'PRAGMA table_info("{tbl}")')
        columns = []
        for row in cur.fetchall():
            # cid, name, type, notnull, dflt_value, pk
            columns.append(
                {
                    "name": row[1],
                    "type": row[2] or "",
                    "notnull": bool(row[3]),
                    "default": row[4],
                    "primary_key": bool(row[5]),
                }
            )
        result.append({"table": tbl, "columns": columns})
    return result


def execute_query(
    conn: sqlite3.Connection, sql: str, params: tuple = ()
) -> dict:
    """اجرای یک کوئری و برگرداندن نتیجه.

    برای SELECT: rows + columns
    برای INSERT/UPDATE/DELETE/CREATE: affected_rows
    """
    cur = conn.cursor()
    try:
        cur.execute(sql, params)
    except sqlite3.Error as exc:
        raise ValueError(f"خطای SQL: {exc}") from exc

    sql_upper = sql.strip().upper()
    if sql_upper.startswith("SELECT") or sql_upper.startswith("PRAGMA"):
        columns = [d[0] for d in cur.description] if cur.description else []
        rows = cur.fetchall()
        return {
            "type": "select",
            "columns": columns,
            "rows": rows,
            "count": len(rows),
        }

    conn.commit()
    return {
        "type": "write",
        "affected": cur.rowcount,
        "lastrowid": cur.lastrowid,
    }


def table_count(conn: sqlite3.Connection, table: str) -> int:
    """تعداد ردیف‌های یک جدول."""
    cur = conn.cursor()
    try:
        cur.execute(f'SELECT COUNT(*) FROM "{table}"')
        return cur.fetchone()[0]
    except sqlite3.Error as exc:
        raise ValueError(f"خطا در خواندن جدول {table}: {exc}") from exc


def export_table_to_csv(
    conn: sqlite3.Connection, table: str, output: Path
) -> int:
    """خروجی CSV از یک جدول. تعداد ردیف‌ها را برمی‌گرداند."""
    cur = conn.cursor()
    try:
        cur.execute(f'SELECT * FROM "{table}"')
    except sqlite3.Error as exc:
        raise ValueError(f"خطا در خواندن جدول {table}: {exc}") from exc

    columns = [d[0] for d in cur.description]
    rows = cur.fetchall()

    with output.open("w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(columns)
        writer.writerows(rows)
    return len(rows)


#CSV Query


def load_csv_to_memory(path: Path, table_name: str = "data") -> tuple[sqlite3.Connection, str]:
    """یک فایل CSV را در دیتابیس SQLite حافظه‌ای بارگذاری می‌کند."""
    conn = sqlite3.connect(":memory:")
    text = path.read_text(encoding="utf-8")
    reader = csv.reader(io.StringIO(text))
    try:
        headers = next(reader)
    except StopIteration:
        raise ValueError("فایل CSV خالی است")

    # همه ستون‌ها TEXT در نظر گرفته می‌شوند
    cols_sql = ", ".join(f'"{h}" TEXT' for h in headers)
    conn.execute(f'CREATE TABLE "{table_name}" ({cols_sql})')

    placeholders = ", ".join("?" for _ in headers)
    insert_sql = f'INSERT INTO "{table_name}" VALUES ({placeholders})'
    rows = [tuple(r) for r in reader if len(r) == len(headers)]
    if rows:
        conn.executemany(insert_sql, rows)
    conn.commit()
    return conn, table_name