"""مدیریت فایل تنظیمات pdev (~/.pdev/config.toml)."""
from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

if sys.version_info >= (3, 11):
    import tomllib
else:  # pragma: no cover
    import tomli as tomllib  # type: ignore

import tomli_w

CONFIG_DIR: Path = Path.home() / ".pdev"
CONFIG_FILE: Path = CONFIG_DIR / "config.toml"

DEFAULT_CONFIG: dict[str, Any] = {
    "general": {
        "quiet": False,
        "verbose": False,
        "language": "fa",
    },
    "shell": {
        "banner": True,
        "history_size": 1000,
        "prompt": "pdev> ",
    },
    "output": {
        "color": True,
    },
}


def ensure_config_dir() -> Path:
    """ساخت پوشهٔ تنظیمات اگر نباشد."""
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    return CONFIG_DIR


def load_config() -> dict:
    """خواندن فایل تنظیمات (اگر نباشد، پیش‌فرض برمی‌گرداند)."""
    if not CONFIG_FILE.exists():
        return dict(DEFAULT_CONFIG)
    try:
        with CONFIG_FILE.open("rb") as f:
            return tomllib.load(f)
    except Exception:
        return dict(DEFAULT_CONFIG)


def save_config(data: dict) -> None:
    """نوشتن تنظیمات به فایل."""
    ensure_config_dir()
    with CONFIG_FILE.open("wb") as f:
        tomli_w.dump(data, f)


def get_value(key: str, default: Any = None) -> Any:
    """خواندن یک مقدار با dot notation. مثال: get_value('shell.banner')"""
    data = load_config()
    for part in key.split("."):
        if isinstance(data, dict) and part in data:
            data = data[part]
        else:
            return default
    return data


def set_value(key: str, value: Any) -> None:
    """نوشتن یک مقدار با dot notation. زیرشاخه‌ها خودکار ساخته می‌شوند."""
    data = load_config()
    parts = key.split(".")
    ref = data
    for p in parts[:-1]:
        if p not in ref or not isinstance(ref[p], dict):
            ref[p] = {}
        ref = ref[p]
    ref[parts[-1]] = value
    save_config(data)


def reset_config() -> None:
    """حذف فایل تنظیمات."""
    if CONFIG_FILE.exists():
        CONFIG_FILE.unlink()