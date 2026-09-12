"""تست‌های Batch 16 — shell، config، plugin."""
from __future__ import annotations

from pathlib import Path
from unittest.mock import patch

import pytest
from typer.testing import CliRunner

from persian_devkit.main import app
from persian_devkit.utils import config_utils, plugin_utils
from persian_devkit.utils.config_utils import (
    DEFAULT_CONFIG,
    get_value,
    load_config,
    reset_config,
    save_config,
    set_value,
)

runner = CliRunner()


#config utils


@pytest.fixture
def temp_config(tmp_path: Path, monkeypatch):
    """تنظیمات را موقتاً به tmp_path منتقل می‌کند."""
    cfg_dir = tmp_path / ".pdev"
    cfg_file = cfg_dir / "config.toml"
    monkeypatch.setattr(config_utils, "CONFIG_DIR", cfg_dir)
    monkeypatch.setattr(config_utils, "CONFIG_FILE", cfg_file)
    return cfg_file


def test_load_config_default(temp_config):
    cfg = load_config()
    assert cfg["shell"]["banner"] is True


def test_save_and_load(temp_config):
    data = {"shell": {"banner": False}, "custom": {"x": 1}}
    save_config(data)
    loaded = load_config()
    assert loaded["shell"]["banner"] is False
    assert loaded["custom"]["x"] == 1


def test_get_value_nested(temp_config):
    save_config({"a": {"b": {"c": 42}}})
    assert get_value("a.b.c") == 42


def test_get_value_missing(temp_config):
    assert get_value("nope.key", default="fallback") == "fallback"


def test_set_value_creates_path(temp_config):
    set_value("new.nested.key", "hello")
    assert get_value("new.nested.key") == "hello"


def test_reset_config(temp_config):
    save_config({"x": 1})
    assert temp_config.exists()
    reset_config()
    assert not temp_config.exists()


#plugin utils


@pytest.fixture
def temp_plugins(tmp_path: Path, monkeypatch):
    """پوشهٔ پلاگین‌ها را موقتاً به tmp_path منتقل می‌کند."""
    pdir = tmp_path / "plugins"
    pdir.mkdir()
    monkeypatch.setattr(plugin_utils, "PLUGINS_DIR", pdir)
    return pdir


def test_discover_plugins_empty(temp_plugins):
    assert plugin_utils.discover_plugins() == []


def test_discover_plugins_with_file(temp_plugins):
    (temp_plugins / "hello.py").write_text('"""سلام"""\n', encoding="utf-8")
    plugins = plugin_utils.discover_plugins()
    assert len(plugins) == 1
    assert plugins[0].name == "hello"
    assert "سلام" in plugins[0].description


def test_discover_skips_underscore(temp_plugins):
    (temp_plugins / "_private.py").write_text("x = 1\n", encoding="utf-8")
    assert plugin_utils.discover_plugins() == []


def test_load_plugin_valid(temp_plugins):
    code = (
        "import typer\n"
        "app = typer.Typer()\n"
    )
    (temp_plugins / "p.py").write_text(code, encoding="utf-8")
    plugin_app = plugin_utils.load_plugin(temp_plugins / "p.py")
    assert plugin_app is not None


def test_load_plugin_no_app(temp_plugins):
    (temp_plugins / "p.py").write_text("x = 1\n", encoding="utf-8")
    assert plugin_utils.load_plugin(temp_plugins / "p.py") is None


def test_load_plugin_missing():
    with pytest.raises(ValueError):
        plugin_utils.load_plugin(Path("no-file.py"))


#CLI


def test_cli_config_path():
    r = runner.invoke(app, ["config", "path"])
    assert r.exit_code == 0
    assert "config.toml" in r.stdout


def test_cli_config_show():
    r = runner.invoke(app, ["config", "show"])
    assert r.exit_code == 0


def test_cli_config_keys():
    r = runner.invoke(app, ["config", "keys"])
    assert r.exit_code == 0
    assert "shell" in r.stdout


def test_cli_plugin_path():
    r = runner.invoke(app, ["plugin", "path"])
    assert r.exit_code == 0
    assert "plugins" in r.stdout.lower()


def test_cli_plugin_list_empty(monkeypatch, tmp_path: Path):
    pdir = tmp_path / "plugins"
    pdir.mkdir()
    monkeypatch.setattr(plugin_utils, "PLUGINS_DIR", pdir)
    r = runner.invoke(app, ["plugin", "list"])
    assert r.exit_code == 0
    assert "هیچ پلاگینی" in r.stdout


def test_cli_plugin_init(monkeypatch, tmp_path: Path):
    pdir = tmp_path / "plugins"
    monkeypatch.setattr(plugin_utils, "PLUGINS_DIR", pdir)
    r = runner.invoke(app, ["plugin", "init"])
    assert r.exit_code == 0
    assert (pdir / "hello.py").exists()


def test_cli_plugin_validate_ok(monkeypatch, tmp_path: Path):
    pdir = tmp_path / "plugins"
    pdir.mkdir()
    (pdir / "sample.py").write_text(
        "import typer\napp = typer.Typer()\n", encoding="utf-8"
    )
    monkeypatch.setattr(plugin_utils, "PLUGINS_DIR", pdir)
    r = runner.invoke(app, ["plugin", "validate", "sample"])
    assert r.exit_code == 0


def test_cli_plugin_validate_missing(monkeypatch, tmp_path: Path):
    pdir = tmp_path / "plugins"
    pdir.mkdir()
    monkeypatch.setattr(plugin_utils, "PLUGINS_DIR", pdir)
    r = runner.invoke(app, ["plugin", "validate", "nope"])
    assert r.exit_code == 1


def test_cli_plugin_validate_no_app(monkeypatch, tmp_path: Path):
    pdir = tmp_path / "plugins"
    pdir.mkdir()
    (pdir / "bad.py").write_text("x = 1\n", encoding="utf-8")
    monkeypatch.setattr(plugin_utils, "PLUGINS_DIR", pdir)
    r = runner.invoke(app, ["plugin", "validate", "bad"])
    assert r.exit_code == 1


def test_cli_plugin_remove(monkeypatch, tmp_path: Path):
    pdir = tmp_path / "plugins"
    pdir.mkdir()
    (pdir / "trash.py").write_text("x = 1\n", encoding="utf-8")
    monkeypatch.setattr(plugin_utils, "PLUGINS_DIR", pdir)
    r = runner.invoke(app, ["plugin", "remove", "trash", "--force"])
    assert r.exit_code == 0
    assert not (pdir / "trash.py").exists()


def test_cli_shell_shows_in_help():
    r = runner.invoke(app, ["--help"])
    assert r.exit_code == 0
    assert "shell" in r.stdout
    assert "config" in r.stdout
    assert "plugin" in r.stdout