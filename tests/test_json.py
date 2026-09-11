"""تست‌های مربوط به JSON."""
import json
from pathlib import Path

import pytest
from typer.testing import CliRunner

from persian_devkit.commands.json_cmd import _flatten
from persian_devkit.main import app

runner = CliRunner()


def test_flatten_nested_dict():
    data = {"a": {"b": 1, "c": {"d": 2}}}
    assert _flatten(data) == {"a.b": 1, "a.c.d": 2}


def test_flatten_list():
    data = {"items": [10, 20, 30]}
    assert _flatten(data) == {
        "items[0]": 10,
        "items[1]": 20,
        "items[2]": 30,
    }


def test_flatten_mixed():
    data = {"user": {"name": "ali", "tags": ["a", "b"]}}
    assert _flatten(data) == {
        "user.name": "ali",
        "user.tags[0]": "a",
        "user.tags[1]": "b",
    }


def test_cli_pretty(tmp_path: Path):
    p = tmp_path / "sample.json"
    p.write_text('{"b":2,"a":1}', encoding="utf-8")
    result = runner.invoke(app, ["json", "pretty", str(p)])
    assert result.exit_code == 0
    assert '"a": 1' in result.stdout


def test_cli_minify(tmp_path: Path):
    p = tmp_path / "sample.json"
    p.write_text('{\n  "a": 1,\n  "b": 2\n}', encoding="utf-8")
    result = runner.invoke(app, ["json", "minify", str(p)])
    assert result.exit_code == 0
    assert '{"a":1,"b":2}' in result.stdout


def test_cli_validate_ok(tmp_path: Path):
    p = tmp_path / "ok.json"
    p.write_text('{"a": 1}', encoding="utf-8")
    result = runner.invoke(app, ["json", "validate", str(p)])
    assert result.exit_code == 0


def test_cli_validate_invalid(tmp_path: Path):
    p = tmp_path / "bad.json"
    p.write_text("{not json}", encoding="utf-8")
    result = runner.invoke(app, ["json", "validate", str(p)])
    assert result.exit_code == 1


def test_cli_keys(tmp_path: Path):
    p = tmp_path / "sample.json"
    p.write_text(json.dumps({"name": "ali", "age": 30}), encoding="utf-8")
    result = runner.invoke(app, ["json", "keys", str(p)])
    assert result.exit_code == 0
    assert "name" in result.stdout
    assert "age" in result.stdout


def test_cli_flatten(tmp_path: Path):
    p = tmp_path / "sample.json"
    p.write_text(json.dumps({"a": {"b": 1}}), encoding="utf-8")
    result = runner.invoke(app, ["json", "flatten", str(p)])
    assert result.exit_code == 0
    assert "a.b" in result.stdout