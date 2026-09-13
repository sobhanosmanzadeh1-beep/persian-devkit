"""تست‌های Batch 17 — doctor، version، info، upgrade."""
from __future__ import annotations

from unittest.mock import patch

import pytest
from typer.testing import CliRunner

from persian_devkit.main import app
from persian_devkit.utils.doctor_utils import (
    CheckResult,
    run_all_checks,
    summary,
)
from persian_devkit.utils.version_utils import (
    _parse_version,
    current_version,
    is_newer,
    latest_version,
)

runner = CliRunner()


#doctor


def test_run_all_checks_returns_list():
    """run_all_checks یک لیست از CheckResult برمی‌گرداند."""
    results = run_all_checks()
    assert isinstance(results, list)
    assert len(results) > 5
    assert all(isinstance(r, CheckResult) for r in results)


def test_all_checks_have_valid_status():
    """هر بررسی یکی از این سه وضعیت را دارد: ok، warn، fail."""
    for r in run_all_checks():
        assert r.status in ("ok", "warn", "fail"), f"وضعیت نامعتبر: {r.status}"


def test_summary_counts():
    """summary تعداد وضعیت‌ها را درست می‌شمارد."""
    results = [
        CheckResult("a", "ok", "x"),
        CheckResult("b", "warn", "x"),
        CheckResult("c", "fail", "x"),
        CheckResult("d", "ok", "x"),
    ]
    s = summary(results)
    assert s["ok"] == 2
    assert s["warn"] == 1
    assert s["fail"] == 1
    assert s["total"] == 4


def test_cli_doctor_runs():
    """pdev doctor بدون خطا اجرا می‌شود."""
    r = runner.invoke(app, ["doctor"])
    # ممکن است exit_code 1 باشد اگر وابستگی اختیاری نصب نباشد
    assert r.exit_code in (0, 1)
    assert "بررسی" in r.stdout


def test_cli_doctor_no_hints():
    """pdev doctor --no-hints بدون بخش راه‌حل اجرا می‌شود."""
    r = runner.invoke(app, ["doctor", "--no-hints"])
    assert r.exit_code in (0, 1)
    assert "راه‌حل‌های پیشنهادی" not in r.stdout


def test_cli_doctor_help():
    """pdev doctor --help کار می‌کند."""
    r = runner.invoke(app, ["doctor", "--help"])
    assert r.exit_code == 0
    assert "doctor" in r.stdout.lower() or "سلامت" in r.stdout


#version


def test_current_version():
    """current_version شمارهٔ نسخهٔ فعلی را برمی‌گرداند."""
    assert current_version() == "2.1.0"


def test_parse_version_simple():
    """_parse_version رشته‌های ساده را درست تبدیل می‌کند."""
    assert _parse_version("1.2.3") == (1, 2, 3)
    assert _parse_version("2.0.0") == (2, 0, 0)
    assert _parse_version("0.1.0") == (0, 1, 0)


def test_parse_version_with_suffix():
    """_parse_version نسخه‌های با پسوند (مثل 1.0.0b1) را مدیریت می‌کند."""
    # عدد قبل از حرف گرفته می‌شود: "0b1" → 0
    assert _parse_version("1.0.0b1") == (1, 0, 0)
    assert _parse_version("2.1.0-alpha") == (2, 1, 0)
    assert _parse_version("1.0.0") == (1, 0, 0)


def test_is_newer_true():
    """is_newer وقتی نسخهٔ جدیدتر است، True برمی‌گرداند."""
    assert is_newer("2.1.0", "2.0.0") is True
    assert is_newer("3.0.0", "2.9.9") is True
    assert is_newer("1.0.1", "1.0.0") is True


def test_is_newer_false():
    """is_newer وقتی نسخهٔ قدیمی‌تر یا مساوی است، False برمی‌گرداند."""
    assert is_newer("2.0.0", "2.0.0") is False
    assert is_newer("1.9.0", "2.0.0") is False
    assert is_newer("2.1.0", "2.1.0") is False


def test_latest_version_network_failure():
    """latest_version در صورت خطای شبکه، None برمی‌گرداند."""
    import httpx

    with patch(
        "persian_devkit.utils.version_utils.httpx.get",
        side_effect=httpx.ConnectError("network error"),
    ):
        result = latest_version(timeout=0.1)
    assert result is None


def test_latest_version_invalid_json():
    """latest_version در صورت JSON نامعتبر، None برمی‌گرداند."""
    class FakeResponse:
        status_code = 200

        def json(self):
            raise ValueError("bad json")

    with patch(
        "persian_devkit.utils.version_utils.httpx.get",
        return_value=FakeResponse(),
    ):
        result = latest_version(timeout=0.1)
    assert result is None


def test_cli_version_short():
    """pdev version --short فقط شماره را نشان می‌دهد."""
    r = runner.invoke(app, ["version", "--short"])
    assert r.exit_code == 0
    assert "2.1.0" in r.stdout


def test_cli_version_full():
    """pdev version اطلاعات کامل را نشان می‌دهد."""
    r = runner.invoke(app, ["version"])
    assert r.exit_code == 0
    assert "2.1.0" in r.stdout
    assert "Python" in r.stdout or "پایتون" in r.stdout


def test_cli_version_help():
    """pdev version --help کار می‌کند."""
    r = runner.invoke(app, ["version", "--help"])
    assert r.exit_code == 0


#info


def test_cli_info_runs():
    """pdev info اجرا می‌شود و اطلاعات پکیج را نشان می‌دهد."""
    r = runner.invoke(app, ["info"])
    assert r.exit_code == 0
    assert "persian-devkit" in r.stdout
    assert "2.1.0" in r.stdout


def test_cli_info_verbose():
    """pdev info -v علاوه بر اطلاعات، لیست زیرفرمان‌ها را نشان می‌دهد."""
    r = runner.invoke(app, ["info", "-v"])
    assert r.exit_code == 0
    assert "زیرفرمان" in r.stdout


def test_cli_info_shows_links():
    """pdev info لینک‌های PyPI و GitHub را نشان می‌دهد."""
    r = runner.invoke(app, ["info"])
    assert r.exit_code == 0
    assert "pypi.org" in r.stdout
    assert "github.com" in r.stdout


def test_cli_info_help():
    """pdev info --help کار می‌کند."""
    r = runner.invoke(app, ["info", "--help"])
    assert r.exit_code == 0


#upgrade


def test_cli_upgrade_check_already_latest():
    """اگر نسخه‌ها برابر باشند، پیام «به‌روز» نمایش داده می‌شود."""
    with patch(
        "persian_devkit.commands.upgrade_cmd.latest_version",
        return_value="2.1.0",
    ):
        r = runner.invoke(app, ["upgrade", "--check"])
    assert r.exit_code == 0
    assert "به‌روز" in r.stdout


def test_cli_upgrade_check_newer_available():
    """اگر نسخهٔ جدیدتر باشد، پیشنهاد ارتقا می‌دهد."""
    with patch(
        "persian_devkit.commands.upgrade_cmd.latest_version",
        return_value="99.0.0",
    ):
        r = runner.invoke(app, ["upgrade", "--check"])
    assert r.exit_code == 0
    assert "99.0.0" in r.stdout


def test_cli_upgrade_no_connection():
    """اگر اتصال به PyPI نباشد، exit_code 1 برمی‌گرداند."""
    with patch(
        "persian_devkit.commands.upgrade_cmd.latest_version",
        return_value=None,
    ):
        r = runner.invoke(app, ["upgrade", "--check"])
    assert r.exit_code == 1
    assert "اتصال" in r.stdout or "PyPI" in r.stdout


def test_cli_upgrade_help():
    """pdev upgrade --help کار می‌کند."""
    r = runner.invoke(app, ["upgrade", "--help"])
    assert r.exit_code == 0


def test_cli_upgrade_prompts_confirmation():
    """pdev upgrade بدون --yes از کاربر تأیید می‌گیرد."""
    with patch(
        "persian_devkit.commands.upgrade_cmd.latest_version",
        return_value="99.0.0",
    ):
        # کاربر جواب "n" می‌دهد → لغو
        r = runner.invoke(app, ["upgrade"], input="n\n")
    assert r.exit_code == 0
    assert "لغو" in r.stdout


#CLI general


def test_all_new_commands_in_help():
    """هر چهار دستور جدید در --help نمایش داده می‌شوند."""
    r = runner.invoke(app, ["--help"])
    assert r.exit_code == 0
    assert "doctor" in r.stdout
    assert "version" in r.stdout
    assert "info" in r.stdout
    assert "upgrade" in r.stdout