"""تست‌های YAML، TOML، CSV و ENV."""
from __future__ import annotations

from pathlib import Path

import pytest
from typer.testing import CliRunner

from persian_devkit.main import app
from persian_devkit.utils.data_utils import (
    dump_env, dump_json, dump_toml, dump_yaml,
    parse_env, parse_json, parse_toml, parse_yaml,
    read_csv, write_csv,
)

runner = CliRunner()


#YAML


def test_yaml_roundtrip():
    data = {"name": "علی", "items": [1, 2, 3], "nested": {"a": True}}
    assert parse_yaml(dump_yaml(data)) == data


def test_yaml_invalid():
    with pytest.raises(ValueError):
        parse_yaml("key: [unclosed")


def test_yaml_persian_dump():
    text = dump_yaml({"greeting": "سلام"})
    assert "سلام" in text  # allow_unicode


#TOML


def test_toml_roundtrip():
    data = {"title": "test", "count": 42, "flag": True}
    assert parse_toml(dump_toml(data)) == data


def test_toml_invalid():
    with pytest.raises(ValueError):
        parse_toml("key = ")


#JSON


def test_json_roundtrip():
    data = {"x": 1, "y": [1, 2]}
    assert parse_json(dump_json(data)) == data


def test_json_invalid():
    with pytest.raises(ValueError):
        parse_json("{not json}")


#CSV


def test_csv_roundtrip(tmp_path: Path):
    headers = ["name", "age"]
    rows = [{"name": "علی", "age": "30"}, {"name": "سارا", "age": "25"}]
    p = tmp_path / "test.csv"
    write_csv(p, headers, rows)
    h, r = read_csv(p)
    assert h == headers
    assert r == rows


def test_csv_delimiter(tmp_path: Path):
    p = tmp_path / "t.csv"
    p.write_text("a;b\n1;2\n", encoding="utf-8")
    h, r = read_csv(p, delimiter=";")
    assert h == ["a", "b"]
    assert r == [{"a": "1", "b": "2"}]


#ENV


def test_env_parse():
    text = "# comment\nFOO=bar\nNAME=\"hello world\"\nEMPTY=\n"
    data = parse_env(text)
    assert data == {"FOO": "bar", "NAME": "hello world", "EMPTY": ""}


def test_env_quoted_single():
    assert parse_env("X='a b'")["X"] == "a b"


def test_env_dump_quotes_spaces():
    text = dump_env({"GREETING": "hello world"})
    assert '"hello world"' in text


def test_env_roundtrip():
    data = {"A": "1", "B": "two words"}
    assert parse_env(dump_env(data)) == data


#CLI yaml


def test_cli_yaml_validate(tmp_path: Path):
    p = tmp_path / "ok.yaml"
    p.write_text("a: 1\nb: 2\n", encoding="utf-8")
    r = runner.invoke(app, ["yaml", "validate", str(p)])
    assert r.exit_code == 0


def test_cli_yaml_validate_invalid(tmp_path: Path):
    p = tmp_path / "bad.yaml"
    p.write_text("a: [unclosed", encoding="utf-8")
    r = runner.invoke(app, ["yaml", "validate", str(p)])
    assert r.exit_code == 1


def test_cli_yaml_to_json(tmp_path: Path):
    p = tmp_path / "x.yaml"
    p.write_text("name: ali\nage: 30\n", encoding="utf-8")
    r = runner.invoke(app, ["yaml", "to-json", str(p)])
    assert r.exit_code == 0
    assert '"name"' in r.stdout


def test_cli_yaml_from_json(tmp_path: Path):
    p = tmp_path / "x.json"
    p.write_text('{"a": 1}', encoding="utf-8")
    r = runner.invoke(app, ["yaml", "from-json", str(p)])
    assert r.exit_code == 0
    assert "a: 1" in r.stdout


def test_cli_yaml_missing():
    r = runner.invoke(app, ["yaml", "validate", "no-file.yaml"])
    assert r.exit_code == 1


#CLI toml


def test_cli_toml_validate(tmp_path: Path):
    p = tmp_path / "ok.toml"
    p.write_text('title = "test"\n', encoding="utf-8")
    r = runner.invoke(app, ["toml", "validate", str(p)])
    assert r.exit_code == 0


def test_cli_toml_validate_invalid(tmp_path: Path):
    p = tmp_path / "bad.toml"
    p.write_text("x = ", encoding="utf-8")
    r = runner.invoke(app, ["toml", "validate", str(p)])
    assert r.exit_code == 1


def test_cli_toml_to_json(tmp_path: Path):
    p = tmp_path / "x.toml"
    p.write_text('name = "ali"\n', encoding="utf-8")
    r = runner.invoke(app, ["toml", "to-json", str(p)])
    assert r.exit_code == 0
    assert "ali" in r.stdout


def test_cli_toml_from_json(tmp_path: Path):
    p = tmp_path / "x.json"
    p.write_text('{"name": "ali"}', encoding="utf-8")
    r = runner.invoke(app, ["toml", "from-json", str(p)])
    assert r.exit_code == 0
    assert 'name = "ali"' in r.stdout


def test_cli_toml_from_json_non_dict(tmp_path: Path):
    p = tmp_path / "x.json"
    p.write_text("[1, 2, 3]", encoding="utf-8")
    r = runner.invoke(app, ["toml", "from-json", str(p)])
    assert r.exit_code == 1


#CLI csv


@pytest.fixture
def sample_csv(tmp_path: Path) -> Path:
    p = tmp_path / "data.csv"
    p.write_text(
        "name,age,city\nعلی,30,تهران\nسارا,25,شیراز\nرضا,40,مشهد\n",
        encoding="utf-8",
    )
    return p


def test_cli_csv_show(sample_csv: Path):
    r = runner.invoke(app, ["csv", "show", str(sample_csv)])
    assert r.exit_code == 0
    assert "علی" in r.stdout
    assert "تهران" in r.stdout


def test_cli_csv_to_json(sample_csv: Path):
    r = runner.invoke(app, ["csv", "to-json", str(sample_csv)])
    assert r.exit_code == 0
    assert '"name": "علی"' in r.stdout


def test_cli_csv_columns(sample_csv: Path):
    r = runner.invoke(app, ["csv", "columns", str(sample_csv)])
    assert r.exit_code == 0
    assert "name" in r.stdout
    assert "3" in r.stdout  # 3 rows


def test_cli_csv_filter(sample_csv: Path):
    r = runner.invoke(app, ["csv", "filter", str(sample_csv), "name", "علی"])
    assert r.exit_code == 0
    assert "1" in r.stdout  # count


def test_cli_csv_filter_bad_column(sample_csv: Path):
    r = runner.invoke(app, ["csv", "filter", str(sample_csv), "nope", "x"])
    assert r.exit_code == 1


def test_cli_csv_filter_bad_regex(sample_csv: Path):
    r = runner.invoke(app, ["csv", "filter", str(sample_csv), "name", "[bad"])
    assert r.exit_code == 1


def test_cli_csv_empty(tmp_path: Path):
    p = tmp_path / "empty.csv"
    p.write_text("", encoding="utf-8")
    r = runner.invoke(app, ["csv", "show", str(p)])
    assert r.exit_code == 0


#CLI env


@pytest.fixture
def sample_env(tmp_path: Path) -> Path:
    p = tmp_path / ".env"
    p.write_text(
        "# config\nAPI_KEY=secret123\nDEBUG=true\nNAME=\"my app\"\n",
        encoding="utf-8",
    )
    return p


def test_cli_env_show_hides_secrets(sample_env: Path):
    r = runner.invoke(app, ["env", "show", str(sample_env)])
    assert r.exit_code == 0
    assert "***" in r.stdout
    assert "secret123" not in r.stdout


def test_cli_env_show_reveal(sample_env: Path):
    r = runner.invoke(app, ["env", "show", str(sample_env), "-r"])
    assert r.exit_code == 0
    assert "secret123" in r.stdout


def test_cli_env_get(sample_env: Path):
    r = runner.invoke(app, ["env", "get", "DEBUG", "-f", str(sample_env)])
    assert r.exit_code == 0
    assert "true" in r.stdout


def test_cli_env_get_missing(sample_env: Path):
    r = runner.invoke(app, ["env", "get", "NOPE", "-f", str(sample_env)])
    assert r.exit_code == 1


def test_cli_env_to_json(sample_env: Path):
    r = runner.invoke(app, ["env", "to-json", str(sample_env)])
    assert r.exit_code == 0
    assert "API_KEY" in r.stdout


def test_cli_env_to_shell(sample_env: Path):
    r = runner.invoke(app, ["env", "to-shell", str(sample_env)])
    assert r.exit_code == 0
    assert "export DEBUG" in r.stdout


def test_cli_env_sort(sample_env: Path):
    r = runner.invoke(app, ["env", "sort", str(sample_env)])
    assert r.exit_code == 0
    # API_KEY باید قبل از DEBUG بیاید
    assert r.stdout.index("API_KEY") < r.stdout.index("DEBUG")


def test_cli_env_missing_file():
    r = runner.invoke(app, ["env", "show", "no-such-file"])
    assert r.exit_code == 1
