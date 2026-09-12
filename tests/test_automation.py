"""تست‌های Batch 14 — خودکارسازی."""
from __future__ import annotations

import sys
from pathlib import Path

import pytest
from typer.testing import CliRunner

from persian_devkit.main import app
from persian_devkit.utils.automation_utils import (
    BatchStep,
    explain_cron,
    parse_batch_file,
    parse_cron,
    repeat_command,
    run_batch,
    run_command,
)

runner = CliRunner()


#run


def test_run_command_echo():
    # دستوری که روی همه سیستم‌عامل‌ها کار می‌کند
    cmd = "echo hello" if sys.platform != "win32" else "echo hello"
    result = run_command(cmd)
    assert result.success
    assert "hello" in result.stdout.lower()


def test_run_command_invalid():
    result = run_command("this-command-does-not-exist-12345")
    assert not result.success


def test_run_command_timeout():
    # دستور cross-platform: پایتون خودش ۱۰ ثانیه صبر می‌کند
    cmd = f'{sys.executable} -c "import time; time.sleep(10)"'
    result = run_command(cmd, timeout=0.5)
    assert result.timed_out


#repeat


def test_repeat_command_basic():
    cmd = "echo test"
    results = repeat_command(cmd, times=3, interval=0)
    assert len(results) == 3
    assert all(r.success for r in results)


def test_repeat_command_stop_on_error():
    # دستور دوم خطا می‌دهد
    results = repeat_command(
        "this-command-fails-999", times=5, stop_on_error=True
    )
    assert len(results) == 1
    assert not results[0].success


def test_repeat_command_invalid_times():
    with pytest.raises(ValueError):
        repeat_command("echo x", times=0)


#batch


def test_parse_batch_file(tmp_path: Path):
    p = tmp_path / "batch.txt"
    p.write_text(
        "# comment\necho one\n\necho two\n!echo fail-but-ignore\n",
        encoding="utf-8",
    )
    steps = parse_batch_file(p)
    assert len(steps) == 3
    assert steps[0].command == "echo one"
    assert steps[2].command == "echo fail-but-ignore"
    assert steps[2].stop_on_error is False


def test_parse_batch_file_missing():
    with pytest.raises(ValueError):
        parse_batch_file(Path("no-file.txt"))


def test_run_batch_basic(tmp_path: Path):
    steps = [
        BatchStep(command="echo a"),
        BatchStep(command="echo b"),
    ]
    results = run_batch(steps)
    assert len(results) == 2
    assert all(r.success for r in results)


def test_run_batch_stops_on_error():
    steps = [
        BatchStep(command="this-fails-999"),
        BatchStep(command="echo never-runs"),
    ]
    results = run_batch(steps)
    assert len(results) == 1
    assert not results[0].success


def test_run_batch_ignore_error():
    steps = [
        BatchStep(command="this-fails-999", stop_on_error=False),
        BatchStep(command="echo runs"),
    ]
    results = run_batch(steps)
    assert len(results) == 2
    assert results[1].success


#cron


def test_parse_cron_basic():
    parsed = parse_cron("0 12 * * *")
    assert parsed["minute"] == [0]
    assert parsed["hour"] == [12]
    assert len(parsed["day"]) == 31
    assert len(parsed["month"]) == 12
    assert len(parsed["weekday"]) == 7


def test_parse_cron_preset_daily():
    parsed = parse_cron("@daily")
    assert parsed["minute"] == [0]
    assert parsed["hour"] == [0]


def test_parse_cron_invalid_preset():
    with pytest.raises(ValueError):
        parse_cron("@nope")


def test_parse_cron_wrong_field_count():
    with pytest.raises(ValueError):
        parse_cron("0 12 * *")


def test_parse_cron_out_of_range():
    with pytest.raises(ValueError):
        parse_cron("0 25 * * *")  # ساعت ۲۵ نامعتبر


def test_parse_cron_range():
    parsed = parse_cron("0 9-17 * * *")
    assert parsed["hour"] == [9, 10, 11, 12, 13, 14, 15, 16, 17]


def test_parse_cron_step():
    parsed = parse_cron("*/15 * * * *")
    assert parsed["minute"] == [0, 15, 30, 45]


def test_explain_cron_basic():
    text = explain_cron("0 12 * * *")
    assert "12" in text


def test_explain_cron_daily():
    text = explain_cron("@daily")
    assert "دقیقه" in text or "ساعت" in text


#CLI


def test_cli_auto_run():
    r = runner.invoke(app, ["auto", "run", "echo hello"])
    assert r.exit_code == 0
    assert "hello" in r.stdout.lower()


def test_cli_auto_run_fails():
    r = runner.invoke(app, ["auto", "run", "this-fails-999"])
    assert r.exit_code != 0


def test_cli_auto_repeat():
    r = runner.invoke(
        app, ["auto", "repeat", "echo x", "-n", "3", "--quiet"]
    )
    assert r.exit_code == 0
    assert "موفق" in r.stdout


def test_cli_auto_repeat_with_fail():
    r = runner.invoke(
        app, ["auto", "repeat", "this-fails-999", "-n", "2", "--quiet"]
    )
    assert r.exit_code == 1


def test_cli_auto_batch(tmp_path: Path):
    p = tmp_path / "b.txt"
    p.write_text("echo one\necho two\n", encoding="utf-8")
    r = runner.invoke(app, ["auto", "batch", str(p)])
    assert r.exit_code == 0
    assert "one" in r.stdout


def test_cli_auto_batch_missing():
    r = runner.invoke(app, ["auto", "batch", "no-file.txt"])
    assert r.exit_code == 1


def test_cli_auto_cron():
    r = runner.invoke(app, ["auto", "cron", "0 12 * * *"])
    assert r.exit_code == 0
    assert "12" in r.stdout


def test_cli_auto_cron_invalid():
    r = runner.invoke(app, ["auto", "cron", "not valid"])
    assert r.exit_code == 1


def test_cli_auto_cron_preset():
    r = runner.invoke(app, ["auto", "cron", "@daily"])
    assert r.exit_code == 0