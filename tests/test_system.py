"""تست‌های Batch 10 — اطلاعات سیستم."""
from __future__ import annotations

from pathlib import Path

from typer.testing import CliRunner

from persian_devkit.main import app
from persian_devkit.utils.system_utils import (
    _HAS_PSUTIL,
    cpu_info,
    disk_info,
    format_bytes,
    memory_info,
    python_info,
    uptime,
)

runner = CliRunner()


#utils


def test_python_info():
    info = python_info()
    assert info["python_version"]
    assert info["system"]
    assert info["architecture"]


def test_disk_info_default():
    info = disk_info()
    assert info["total"] > 0
    assert 0 <= info["percent"] <= 100


def test_disk_info_explicit_path():
    info = disk_info(Path.home())
    assert info["free"] > 0


def test_format_bytes_small():
    assert format_bytes(0) == "0.00 B"
    assert format_bytes(512) == "512.00 B"


def test_format_bytes_kb():
    assert "KB" in format_bytes(2048)


def test_format_bytes_gb():
    assert "GB" in format_bytes(2 * 1024 ** 3)


def test_memory_info():
    if not _HAS_PSUTIL:
        return
    info = memory_info()
    assert info["total"] > 0
    assert 0 <= info["percent"] <= 100


def test_cpu_info():
    if not _HAS_PSUTIL:
        return
    info = cpu_info()
    assert info["logical_cores"] >= 1


def test_uptime():
    if not _HAS_PSUTIL:
        return
    up = uptime()
    assert up.total_seconds() > 0


#CLI


def test_cli_sys_python():
    r = runner.invoke(app, ["sys", "python"])
    assert r.exit_code == 0
    assert "python_version" in r.stdout


def test_cli_sys_disk():
    r = runner.invoke(app, ["sys", "disk"])
    assert r.exit_code == 0
    assert "کل" in r.stdout
    assert "آزاد" in r.stdout


def test_cli_sys_all():
    r = runner.invoke(app, ["sys", "all"])
    assert r.exit_code == 0
    assert "سیستم عامل" in r.stdout


def test_cli_sys_memory():
    if not _HAS_PSUTIL:
        return
    r = runner.invoke(app, ["sys", "memory"])
    assert r.exit_code == 0
    assert "حافظه" in r.stdout


def test_cli_sys_cpu():
    if not _HAS_PSUTIL:
        return
    r = runner.invoke(app, ["sys", "cpu"])
    assert r.exit_code == 0


def test_cli_sys_uptime():
    if not _HAS_PSUTIL:
        return
    r = runner.invoke(app, ["sys", "uptime"])
    assert r.exit_code == 0


def test_cli_sys_top():
    if not _HAS_PSUTIL:
        return
    r = runner.invoke(app, ["sys", "top", "-n", "3"])
    assert r.exit_code == 0


def test_cli_sys_top_invalid_by():
    if not _HAS_PSUTIL:
        return
    r = runner.invoke(app, ["sys", "top", "-b", "invalid"])
    assert r.exit_code == 1