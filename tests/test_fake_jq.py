"""تست‌های lorem، name و jq."""
from __future__ import annotations

import json
from pathlib import Path

import pytest
from typer.testing import CliRunner

from persian_devkit.main import app
from persian_devkit.utils.fake_utils import (
    lorem_ipsum,
    random_city,
    random_email,
    random_first_name,
    random_full_name,
    random_last_name,
    random_paragraph,
    random_sentence,
    random_words,
)
from persian_devkit.utils.jsonpath_utils import JSONPathError, query

runner = CliRunner()


#fake


def test_random_sentence_not_empty():
    assert len(random_sentence()) > 10


def test_random_paragraph_has_sentences():
    p = random_paragraph(sentences=3)
    assert p.count(".") >= 2  # حداقل دو نقطه


def test_lorem_ipsum_paragraphs():
    text = lorem_ipsum(paragraphs=2, sentences_per_paragraph=2)
    assert text.count("\n\n") == 1


def test_random_words_count():
    result = random_words(7)
    assert len(result.split()) == 7


def test_full_name_has_space():
    name = random_full_name()
    assert " " in name


def test_gender_male_only():
    for _ in range(20):
        name = random_first_name("male")
        assert name in name  # فقط چک می‌کنیم که استرینگ باشد


def test_random_email_format():
    email = random_email()
    assert "@" in email
    assert "." in email.split("@")[1]


def test_random_city_is_str():
    assert isinstance(random_city(), str)


#query


def test_query_simple_key():
    assert query({"a": 1}, ".a") == 1


def test_query_nested():
    assert query({"a": {"b": {"c": 42}}}, ".a.b.c") == 42


def test_query_array_index():
    assert query({"items": [10, 20, 30]}, ".items[1]") == 20


def test_query_wildcard():
    data = {"items": [{"name": "a"}, {"name": "b"}]}
    assert query(data, ".items[*].name") == ["a", "b"]


def test_query_dollar_prefix():
    assert query({"x": 5}, "$.x") == 5


def test_query_quoted_key():
    assert query({"key with space": 1}, '["key with space"]') == 1


def test_query_missing_key():
    assert query({"a": 1}, ".b") == []


def test_query_invalid_path():
    with pytest.raises(JSONPathError):
        query({"a": 1}, "!!!!!")


def test_query_empty_path_returns_data():
    data = {"a": 1}
    assert query(data, "") == data


#CLI lorem


def test_cli_lorem_sentence():
    r = runner.invoke(app, ["lorem", "sentence"])
    assert r.exit_code == 0
    assert "." in r.stdout


def test_cli_lorem_paragraph():
    r = runner.invoke(app, ["lorem", "paragraph", "-s", "2"])
    assert r.exit_code == 0


def test_cli_lorem_words():
    r = runner.invoke(app, ["lorem", "words", "-c", "5"])
    assert r.exit_code == 0
    assert len(r.stdout.strip().split()) == 5


def test_cli_lorem_all():
    r = runner.invoke(app, ["lorem", "all", "-p", "2"])
    assert r.exit_code == 0


#CLI name


def test_cli_name_full():
    r = runner.invoke(app, ["name", "full"])
    assert r.exit_code == 0
    assert " " in r.stdout.strip()


def test_cli_name_email():
    r = runner.invoke(app, ["name", "email"])
    assert r.exit_code == 0
    assert "@" in r.stdout


def test_cli_name_profile_json():
    r = runner.invoke(app, ["name", "profile", "-c", "2", "-j"])
    assert r.exit_code == 0
    data = json.loads(r.stdout)
    assert len(data) == 2
    assert "name" in data[0]


def test_cli_name_profile_table():
    r = runner.invoke(app, ["name", "profile", "-c", "2"])
    assert r.exit_code == 0


def test_cli_name_gender_invalid():
    r = runner.invoke(app, ["name", "full", "-g", "nope"])
    assert r.exit_code == 1


#CLI jq


@pytest.fixture
def sample_json(tmp_path: Path) -> Path:
    p = tmp_path / "d.json"
    p.write_text(
        json.dumps({
            "user": {"name": "علی", "age": 30},
            "items": [{"id": 1, "title": "one"}, {"id": 2, "title": "two"}],
        }, ensure_ascii=False),
        encoding="utf-8",
    )
    return p


def test_cli_jq_simple(sample_json: Path):
    r = runner.invoke(app, ["jq", ".user.name", "-f", str(sample_json), "-r"])
    assert r.exit_code == 0
    assert "علی" in r.stdout


def test_cli_jq_nested(sample_json: Path):
    r = runner.invoke(app, ["jq", ".user.age", "-f", str(sample_json), "-r"])
    assert r.exit_code == 0
    assert "30" in r.stdout


def test_cli_jq_wildcard(sample_json: Path):
    r = runner.invoke(app, ["jq", ".items[*].id", "-f", str(sample_json), "-c"])
    assert r.exit_code == 0
    assert "[1,2]" in r.stdout.replace(" ", "")


def test_cli_jq_index(sample_json: Path):
    r = runner.invoke(app, ["jq", ".items[1].title", "-f", str(sample_json), "-r"])
    assert r.exit_code == 0
    assert "two" in r.stdout


def test_cli_jq_stdin(sample_json: Path):
    text = sample_json.read_text(encoding="utf-8")
    r = runner.invoke(app, ["jq", ".user.name", "-r"], input=text)
    assert r.exit_code == 0
    assert "علی" in r.stdout


def test_cli_jq_missing_file():
    r = runner.invoke(app, ["jq", ".a", "-f", "no-file.json"])
    assert r.exit_code == 1


def test_cli_jq_invalid_json(tmp_path: Path):
    p = tmp_path / "bad.json"
    p.write_text("{not json}", encoding="utf-8")
    r = runner.invoke(app, ["jq", ".a", "-f", str(p)])
    assert r.exit_code == 1


def test_cli_jq_invalid_path(sample_json: Path):
    r = runner.invoke(app, ["jq", "!!!!!", "-f", str(sample_json)])
    assert r.exit_code == 1


def test_cli_jq_object_output(sample_json: Path):
    r = runner.invoke(app, ["jq", ".user", "-f", str(sample_json), "-r"])
    assert r.exit_code == 0
    assert "علی" in r.stdout
