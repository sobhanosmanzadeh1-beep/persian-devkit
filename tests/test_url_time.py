"""تست‌های URL، زمان، و متن پیشرفته."""
from datetime import datetime, timezone

import pytest
from typer.testing import CliRunner

from persian_devkit.main import app
from persian_devkit.utils.text_utils import change_case, diff_lines, regex_test, to_slug
from persian_devkit.utils.time_utils import (
    from_unix,
    humanize_duration,
    now_unix,
    parse_duration,
    to_unix,
)
from persian_devkit.utils.url_utils import (
    build_query,
    decode_query,
    parse_url,
    url_decode,
    url_encode,
)

runner = CliRunner()


#slug


def test_slug_persian():
    assert to_slug("سلام دنیا") == "سلام-دنیا"


def test_slug_with_halfspace():
    assert to_slug("می‌روم") == "می-روم"


def test_slug_with_punctuation():
    assert to_slug("Hello, World! 2024") == "hello-world-2024"


def test_slug_max_length():
    result = to_slug("یک متن بسیار طولانی برای تست", max_length=10)
    assert len(result) <= 10


def test_slug_separator():
    assert to_slug("a b c", separator="_") == "a_b_c"


#case


def test_case_upper():
    assert change_case("hello", "upper") == "HELLO"


def test_case_lower():
    assert change_case("HELLO", "lower") == "hello"


def test_case_title():
    assert change_case("hello world", "title") == "Hello World"


def test_case_swap():
    assert change_case("AbC", "swap") == "aBc"


def test_case_invalid():
    with pytest.raises(ValueError):
        change_case("x", "nope")


#diff


def test_diff_identical():
    assert diff_lines("abc", "abc") == []


def test_diff_change():
    result = diff_lines("line1\nline2", "line1\nline3")
    signs = [s for s, _ in result]
    assert "-" in signs
    assert "+" in signs


#regex


def test_regex_match():
    r = regex_test(r"\d+", "a1b22c333")
    assert r["count"] == 3
    assert "333" in r["matches"]


def test_regex_no_match():
    r = regex_test(r"\d+", "abc")
    assert r["count"] == 0
    assert r["is_match"] is False


def test_regex_invalid():
    with pytest.raises(ValueError):
        regex_test("[invalid(", "text")


#url


def test_url_encode_ascii():
    assert url_encode("hello world") == "hello%20world"


def test_url_encode_persian():
    result = url_encode("سلام")
    assert "%D8" in result


def test_url_decode_roundtrip():
    assert url_decode(url_encode("سلام دنیا")) == "سلام دنیا"


def test_parse_url_full():
    r = parse_url("https://user:pass@example.com:8080/path?x=1&y=2#frag")
    assert r["scheme"] == "https"
    assert r["host"] == "example.com"
    assert r["port"] == 8080
    assert r["path"] == "/path"
    assert r["query"] == {"x": "1", "y": "2"}
    assert r["fragment"] == "frag"


def test_build_query():
    assert build_query({"a": "1", "b": "2"}) == "a=1&b=2"


def test_decode_query_multi():
    r = decode_query("a=1&a=2&b=3")
    assert r["a"] == ["1", "2"]
    assert r["b"] == ["3"]


#time


def test_parse_duration_short():
    assert parse_duration("2h30m") == 2 * 3600 + 30 * 60


def test_parse_duration_persian():
    assert parse_duration("2 ساعت و 30 دقیقه") == 2 * 3600 + 30 * 60


def test_parse_duration_invalid():
    with pytest.raises(ValueError):
        parse_duration("nonsense")


def test_humanize_duration():
    assert "1 ساعت" in humanize_duration(3661)
    assert "منفی" in humanize_duration(-60)


def test_to_from_unix_roundtrip():
    dt = datetime(2024, 3, 21, 12, 0, 0, tzinfo=timezone.utc)
    ts = to_unix(dt)
    assert from_unix(ts) == dt


def test_now_unix_is_reasonable():
    ts = now_unix()
    assert ts > 1_700_000_000  # > Nov 2023


#CLI


def test_cli_text_slug():
    r = runner.invoke(app, ["text", "slug", "سلام دنیا"])
    assert r.exit_code == 0
    assert "سلام-دنیا" in r.stdout


def test_cli_text_case():
    r = runner.invoke(app, ["text", "case", "upper", "hello"])
    assert r.exit_code == 0
    assert "HELLO" in r.stdout


def test_cli_text_case_invalid():
    r = runner.invoke(app, ["text", "case", "nope", "hello"])
    assert r.exit_code == 1


def test_cli_text_diff():
    r = runner.invoke(app, ["text", "diff", "abc", "abd"])
    assert r.exit_code == 0


def test_cli_text_regex():
    r = runner.invoke(app, ["text", "regex", r"\d+", "a1b22"])
    assert r.exit_code == 0
    assert "2" in r.stdout  # count


def test_cli_url_encode():
    r = runner.invoke(app, ["url", "encode", "hello world"])
    assert r.exit_code == 0
    assert "hello%20world" in r.stdout


def test_cli_url_decode():
    r = runner.invoke(app, ["url", "decode", "hello%20world"])
    assert r.exit_code == 0
    assert "hello world" in r.stdout


def test_cli_url_parse():
    r = runner.invoke(app, ["url", "parse", "https://x.com:8080/a?b=1"])
    assert r.exit_code == 0
    assert "https" in r.stdout
    assert "x.com" in r.stdout


def test_cli_url_build():
    r = runner.invoke(app, ["url", "build", "a=1", "b=2"])
    assert r.exit_code == 0
    assert "a=1" in r.stdout


def test_cli_url_build_invalid():
    r = runner.invoke(app, ["url", "build", "noequals"])
    assert r.exit_code == 1


def test_cli_time_now():
    r = runner.invoke(app, ["time", "now"])
    assert r.exit_code == 0


def test_cli_time_from_unix():
    r = runner.invoke(app, ["time", "from-unix", "0"])
    assert r.exit_code == 0
    assert "1970" in r.stdout


def test_cli_time_to_unix():
    r = runner.invoke(app, ["time", "to-unix", "2024-01-01"])
    assert r.exit_code == 0


def test_cli_time_to_unix_invalid():
    r = runner.invoke(app, ["time", "to-unix", "not-a-date"])
    assert r.exit_code == 1


def test_cli_time_duration():
    r = runner.invoke(app, ["time", "duration", "1h30m"])
    assert r.exit_code == 0
    assert "5,400" in r.stdout


def test_cli_time_duration_seconds():
    r = runner.invoke(app, ["time", "duration", "90s"])
    assert r.exit_code == 0
    assert "90" in r.stdout


def test_cli_time_duration_invalid():
    r = runner.invoke(app, ["time", "duration", "garbage"])
    assert r.exit_code == 1


def test_cli_time_ago():
    r = runner.invoke(app, ["time", "ago", "0"])
    assert r.exit_code == 0