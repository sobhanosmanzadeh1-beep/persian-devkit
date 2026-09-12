"""کشف و بارگذاری پلاگین‌های pdev از ~/.pdev/plugins/."""
from __future__ import annotations

import ast
import importlib.util
import os
import sys
from dataclasses import dataclass, field
from pathlib import Path

PLUGINS_DIR: Path = Path.home() / ".pdev" / "plugins"


@dataclass
class PluginInfo:
    """اطلاعات یک پلاگین."""

    name: str
    path: Path
    description: str = ""


def ensure_plugins_dir() -> Path:
    """ساخت پوشهٔ پلاگین‌ها."""
    PLUGINS_DIR.mkdir(parents=True, exist_ok=True)
    return PLUGINS_DIR


def _extract_docstring(source: str) -> str:
    """اولین خط docstring فایل را برمی‌گرداند."""
    try:
        tree = ast.parse(source)
        doc = ast.get_docstring(tree)
        if doc:
            return doc.strip().splitlines()[0]
    except (SyntaxError, ValueError):
        pass
    return ""


def discover_plugins() -> list[PluginInfo]:
    """لیست پلاگین‌های موجود (بدون بارگذاری)."""
    if not PLUGINS_DIR.exists():
        return []

    results: list[PluginInfo] = []
    for p in sorted(PLUGINS_DIR.glob("*.py")):
        if p.name.startswith("_"):
            continue
        description = ""
        try:
            description = _extract_docstring(p.read_text(encoding="utf-8"))
        except OSError:
            continue
        results.append(PluginInfo(name=p.stem, path=p, description=description))
    return results


def load_plugin(path: Path):
    """بارگذاری یک پلاگین و برگرداندن Typer app آن (یا None)."""
    import typer

    if not path.exists():
        raise ValueError(f"پلاگین یافت نشد: {path}")

    module_name = f"persian_devkit_plugin_{path.stem}"
    spec = importlib.util.spec_from_file_location(module_name, path)
    if spec is None or spec.loader is None:
        raise ValueError(f"نمی‌توان پلاگین را بارگذاری کرد: {path}")

    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    try:
        spec.loader.exec_module(module)
    except Exception as exc:
        raise ValueError(f"خطا در اجرای پلاگین {path.name}: {exc}") from exc

    plugin_app = getattr(module, "app", None)
    if plugin_app is None or not isinstance(plugin_app, typer.Typer):
        return None
    return plugin_app


def register_plugins(app, *, fail_silent: bool = True) -> list[str]:
    """همهٔ پلاگین‌ها را روی اپ اصلی ثبت می‌کند.

    با env var ``PDEV_NO_PLUGINS=1`` غیرفعال می‌شود.
    خروجی: لیست نام‌های ثبت‌شده.
    """
    if os.environ.get("PDEV_NO_PLUGINS"):
        return []

    registered: list[str] = []
    for info in discover_plugins():
        try:
            plugin_app = load_plugin(info.path)
        except Exception as exc:
            if not fail_silent:
                raise
            print(
                f"هشدار: خطا در بارگذاری پلاگین {info.name}: {exc}",
                file=sys.stderr,
            )
            continue

        if plugin_app is None:
            if not fail_silent:
                raise ValueError(
                    f"پلاگین {info.name} متغیر `app: typer.Typer` ندارد."
                )
            continue

        app.add_typer(
            plugin_app,
            name=info.name,
            help=info.description or f" پلاگین: {info.name}",
        )
        registered.append(info.name)
    return registered