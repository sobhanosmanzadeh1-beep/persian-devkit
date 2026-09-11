"""تست‌های یکپارچگی برای همهٔ زیرفرمان‌های pdev."""
from __future__ import annotations

import json
from pathlib import Path

import pytest
from typer.testing import CliRunner

from persian_devkit.main import app

runner = CliRunner()


#general


def test_version_flag():
    result = runner.invoke(app, ["--version"])
    assert result.exit_code == 0
    assert "persian-devkit" in result.stdout


def test_help_shows_all_commands():
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    for name in ("date", "number", "text", "uuid", "json"):
        assert name in result.stdout


#date


def test_date_to_jalali():
    result = runner.invoke(app, ["date", "to-jalali", "2024-03-21"])
    assert result.exit_code == 0
    assert "1403/01/02" in result.stdout


def test_date_to_jalali_invalid():
    result = runner.invoke(app, ["date", "to-jalali", "not-a-date"])
    assert result.exit_code == 1
    assert "خطا" in result.stdout


def test_date_to_gregorian():
    result = runner.invoke(app, ["date", "to-gregorian", "1403/01/02"])
    assert result.exit_code == 0
    assert "2024-03-21" in result.stdout


def test_date_to_gregorian_invalid():
    result = runner.invoke(app, ["date", "to-gregorian", "abcd"])
    assert result.exit_code == 1


def test_date_now():
    result = runner.invoke(app, ["date", "now"])
    assert result.exit_code == 0
    assert "میلادی" in result.stdout
    assert "شمسی" in result.stdout


def test_date_diff():
    result = runner.invoke(app, ["date", "diff", "1402/01/01", "1403/01/01"])
    assert result.exit_code == 0
    assert "365" in result.stdout


def test_date_diff_invalid():
    result = runner.invoke(app, ["date", "diff", "bad", "worse"])
    assert result.exit_code == 1


#number


def test_number_to_persian():
    result = runner.invoke(app, ["number", "to-persian", "1234567"])
    assert result.exit_code == 0
    assert "۱۲۳۴۵۶۷" in result.stdout


def test_number_to_english():
    result = runner.invoke(app, ["number", "to-english", "۱۲۳۴۵۶۷"])
    assert result.exit_code == 0
    assert "1234567" in result.stdout


def test_number_format_int():
    result = runner.invoke(app, ["number", "format", "1234567"])
    assert result.exit_code == 0
    assert "1,234,567" in result.stdout


def test_number_format_float():
    result = runner.invoke(app, ["number", "format", "1234.5"])
    assert result.exit_code == 0
    assert "1,234.50" in result.stdout


def test_number_format_invalid():
    result = runner.invoke(app, ["number", "format", "abc"])
    assert result.exit_code == 1


def test_number_words():
    result = runner.invoke(app, ["number", "words", "1234"])
    assert result.exit_code == 0
    assert "یک هزار" in result.stdout


def test_number_words_invalid():
    result = runner.invoke(app, ["number", "words", "abc"])
    assert result.exit_code == 1


#text


def test_text_halfspace():
    result = runner.invoke(app, ["text", "halfspace", "می روم"])
    assert result.exit_code == 0
    assert "می\u200cروم" in result.stdout


def test_text_normalize():
    result = runner.invoke(app, ["text", "normalize", "سلام  دنیا"])
    assert result.exit_code == 0
    assert "سلام دنیا" in result.stdout


def test_text_reverse():
    result = runner.invoke(app, ["text", "reverse", "abc"])
    assert result.exit_code == 0
    assert "cba" in result.stdout


def test_text_stats():
    result = runner.invoke(app, ["text", "stats", "یک متن نمونه"])
    assert result.exit_code == 0
    assert "کلمات" in result.stdout
    assert "کاراکترها" in result.stdout


def test_text_reads_stdin():
    result = runner.invoke(app, ["text", "halfspace"], input="می روم")
    assert result.exit_code == 0
    assert "می\u200cروم" in result.stdout

#uuid


def test_uuid_new():
    result = runner.invoke(app, ["uuid", "new"])
    assert result.exit_code == 0
    # UUID4 format: 8-4-4-4-12
    line = result.stdout.strip().splitlines()[-1]
    assert len(line) == 36
    assert line.count("-") == 4


def test_uuid_new_count():
    result = runner.invoke(app, ["uuid", "new", "--count", "3"])
    assert result.exit_code == 0
    lines = [ln for ln in result.stdout.strip().splitlines() if ln]
    assert len(lines) == 3


def test_uuid_new_upper():
    result = runner.invoke(app, ["uuid", "new", "--upper"])
    assert result.exit_code == 0
    line = result.stdout.strip().splitlines()[-1]
    assert line == line.upper()


def test_uuid_short():
    result = runner.invoke(app, ["uuid", "short"])
    assert result.exit_code == 0
    line = result.stdout.strip().splitlines()[-1]
    assert len(line) == 22


def test_uuid_short_count():
    result = runner.invoke(app, ["uuid", "short", "--count", "4"])
    assert result.exit_code == 0
    lines = [ln for ln in result.stdout.strip().splitlines() if ln]
    assert len(lines) == 4


#json


@pytest.fixture
def sample_json(tmp_path: Path) -> Path:
    p = tmp_path / "sample.json"
    p.write_text(
        json.dumps({"b": 2, "a": {"c": 1, "d": [10, 20]}}),
        encoding="utf-8",
    )
    return p


def test_json_pretty(sample_json: Path):
    result = runner.invoke(app, ["json", "pretty", str(sample_json)])
    assert result.exit_code == 0
    assert '"a"' in result.stdout


def test_json_pretty_output(sample_json: Path, tmp_path: Path):
    out = tmp_path / "out.json"
    result = runner.invoke(
        app, ["json", "pretty", str(sample_json), "-o", str(out)]
    )
    assert result.exit_code == 0
    assert out.exists()
    assert '"a"' in out.read_text(encoding="utf-8")


def test_json_minify(sample_json: Path):
    result = runner.invoke(app, ["json", "minify", str(sample_json)])
    assert result.exit_code == 0
    # minified has no spaces after separators
    assert '", "' not in result.stdout


def test_json_minify_output(sample_json: Path, tmp_path: Path):
    out = tmp_path / "min.json"
    result = runner.invoke(
        app, ["json", "minify", str(sample_json), "-o", str(out)]
    )
    assert result.exit_code == 0
    assert out.exists()


def test_json_validate_ok(sample_json: Path):
    result = runner.invoke(app, ["json", "validate", str(sample_json)])
    assert result.exit_code == 0


def test_json_validate_bad(tmp_path: Path):
    p = tmp_path / "bad.json"
    p.write_text("{not json}", encoding="utf-8")
    result = runner.invoke(app, ["json", "validate", str(p)])
    assert result.exit_code == 1


def test_json_validate_missing():
    result = runner.invoke(app, ["json", "validate", "no-such-file.json"])
    assert result.exit_code == 1


def test_json_keys(sample_json: Path):
    result = runner.invoke(app, ["json", "keys", str(sample_json)])
    assert result.exit_code == 0
    assert "a" in result.stdout
    assert "b" in result.stdout


def test_json_keys_non_dict(tmp_path: Path):
    p = tmp_path / "list.json"
    p.write_text("[1, 2, 3]", encoding="utf-8")
    result = runner.invoke(app, ["json", "keys", str(p)])
    assert result.exit_code == 1


def test_json_flatten(sample_json: Path):
    result = runner.invoke(app, ["json", "flatten", str(sample_json)])
    assert result.exit_code == 0
    assert "a.c" in result.stdout
    assert "a.d[0]" in result.stdout


def test_json_pretty_invalid(tmp_path: Path):
    p = tmp_path / "bad.json"
    p.write_text("{oops", encoding="utf-8")
    result = runner.invoke(app, ["json", "pretty", str(p)])
    assert result.exit_code == 1