"""تست‌های Batch 12 — دیتابیس."""
from __future__ import annotations

import sqlite3
from pathlib import Path

import pytest
from typer.testing import CliRunner

from persian_devkit.main import app
from persian_devkit.utils.db_utils import (
    execute_query,
    export_table_to_csv,
    get_schema,
    list_tables,
    load_csv_to_memory,
    open_db,
    table_count,
)

runner = CliRunner()


@pytest.fixture
def sample_db(tmp_path: Path) -> Path:
    db = tmp_path / "test.db"
    conn = sqlite3.connect(str(db))
    conn.execute("CREATE TABLE users (id INTEGER PRIMARY KEY, name TEXT, age INTEGER)")
    conn.execute("INSERT INTO users (name, age) VALUES (?, ?)", ("علی", 30))
    conn.execute("INSERT INTO users (name, age) VALUES (?, ?)", ("سارا", 25))
    conn.commit()
    conn.close()
    return db


#utils


def test_list_tables(sample_db: Path):
    with open_db(sample_db) as conn:
        assert "users" in list_tables(conn)


def test_get_schema(sample_db: Path):
    with open_db(sample_db) as conn:
        schemas = get_schema(conn, "users")
        assert len(schemas) == 1
        cols = [c["name"] for c in schemas[0]["columns"]]
        assert "id" in cols and "name" in cols


def test_table_count(sample_db: Path):
    with open_db(sample_db) as conn:
        assert table_count(conn, "users") == 2


def test_execute_select(sample_db: Path):
    with open_db(sample_db) as conn:
        result = execute_query(conn, "SELECT * FROM users")
        assert result["type"] == "select"
        assert result["count"] == 2


def test_execute_insert(sample_db: Path):
    with open_db(sample_db) as conn:
        result = execute_query(conn, "INSERT INTO users (name) VALUES ('رضا')")
        assert result["type"] == "write"
        assert result["affected"] == 1


def test_execute_invalid_sql(sample_db: Path):
    with open_db(sample_db) as conn:
        with pytest.raises(ValueError):
            execute_query(conn, "INVALID SQL HERE")


def test_export_table_to_csv(sample_db: Path, tmp_path: Path):
    out = tmp_path / "users.csv"
    with open_db(sample_db) as conn:
        count = export_table_to_csv(conn, "users", out)
    assert count == 2
    assert out.exists()


def test_load_csv_to_memory(tmp_path: Path):
    p = tmp_path / "data.csv"
    p.write_text("name,age\nعلی,30\nسارا,25\n", encoding="utf-8")
    conn, table = load_csv_to_memory(p)
    assert table == "data"
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM data")
    assert cur.fetchone()[0] == 2
    conn.close()


def test_load_csv_empty(tmp_path: Path):
    p = tmp_path / "empty.csv"
    p.write_text("", encoding="utf-8")
    with pytest.raises(ValueError):
        load_csv_to_memory(p)


#CLI


def test_cli_sqlite_tables(sample_db: Path):
    r = runner.invoke(app, ["sqlite", "tables", str(sample_db)])
    assert r.exit_code == 0
    assert "users" in r.stdout


def test_cli_sqlite_schema(sample_db: Path):
    r = runner.invoke(app, ["sqlite", "schema", str(sample_db), "-t", "users"])
    assert r.exit_code == 0
    assert "id" in r.stdout
    assert "name" in r.stdout


def test_cli_sqlite_query(sample_db: Path):
    r = runner.invoke(
        app, ["sqlite", "query", str(sample_db), "SELECT * FROM users"]
    )
    assert r.exit_code == 0
    assert "علی" in r.stdout


def test_cli_sqlite_query_invalid(sample_db: Path):
    r = runner.invoke(
        app, ["sqlite", "query", str(sample_db), "NOT VALID SQL"]
    )
    assert r.exit_code == 1


def test_cli_sqlite_missing_file():
    r = runner.invoke(app, ["sqlite", "tables", "no-file.db"])
    assert r.exit_code == 1


def test_cli_sqlite_export(sample_db: Path, tmp_path: Path):
    out = tmp_path / "out.csv"
    r = runner.invoke(
        app, ["sqlite", "export", str(sample_db), "users", str(out)]
    )
    assert r.exit_code == 0
    assert out.exists()


def test_cli_csv_query(tmp_path: Path):
    p = tmp_path / "data.csv"
    p.write_text("name,age\nعلی,30\nسارا,25\n", encoding="utf-8")
    r = runner.invoke(
        app,
        ["csv-query", "query", str(p), "SELECT name FROM data WHERE age > '26'"],
    )
    assert r.exit_code == 0
    assert "علی" in r.stdout


def test_cli_csv_query_columns(tmp_path: Path):
    p = tmp_path / "data.csv"
    p.write_text("name,age\n", encoding="utf-8")
    r = runner.invoke(app, ["csv-query", "columns", str(p)])
    assert r.exit_code == 0
    assert "name" in r.stdout
    assert "age" in r.stdout


def test_cli_csv_query_missing():
    r = runner.invoke(app, ["csv-query", "query", "no-file.csv", "SELECT 1"])
    assert r.exit_code == 1