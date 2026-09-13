"""توابع بررسی سلامت نصب و محیط pdev."""
from __future__ import annotations

import importlib
import platform
import sys
from dataclasses import dataclass

from persian_devkit import __version__


@dataclass
class CheckResult:
    """نتیجهٔ یک بررسی."""

    name: str
    status: str  # "ok" | "warn" | "fail"
    message: str
    fix_hint: str = ""


def _check_python_version() -> CheckResult:
    """بررسی نسخهٔ پایتون."""
    v = sys.version_info
    version_str = f"{v.major}.{v.minor}.{v.micro}"
    if v >= (3, 10):
        return CheckResult("Python version", "ok", f"Python {version_str}")
    return CheckResult(
        "Python version",
        "fail",
        f"Python {version_str} — حداقل نسخه 3.10 لازم است",
        "Python را به 3.10+ ارتقا بده",
    )


def _check_package_version() -> CheckResult:
    """بررسی نصب پکیج."""
    return CheckResult(
        "Package",
        "ok",
        f"persian-devkit {__version__} نصب است",
    )


_REQUIRED = ["typer", "rich", "jdatetime", "bidi"]
_OPTIONAL = {
    "psutil": "برای pdev sys",
    "pypdf": "برای pdev pdf",
    "mutagen": "برای pdev audio",
    "hijridate": "برای pdev hijri",
    "yaml": "برای pdev yaml",
    "tomli_w": "برای pdev toml",
    "httpx": "برای pdev http/ip",
    "qrcode": "برای pdev qrcode",
    "PIL": "برای pdev image",
}


def _check_dependency(name: str, required: bool, purpose: str = "") -> CheckResult:
    """بررسی نصب یک وابستگی."""
    try:
        mod = importlib.import_module(name)
        version = getattr(mod, "__version__", "?")
        label = name if not purpose else f"{name} ({purpose})"
        return CheckResult(label, "ok", f"نسخه {version}")
    except ImportError:
        label = name if not purpose else f"{name} ({purpose})"
        if required:
            return CheckResult(
                label,
                "fail",
                "نصب نیست",
                f"pip install {name}",
            )
        return CheckResult(
            label,
            "warn",
            "نصب نیست (اختیاری)",
            f"pip install {name}",
        )


def _check_config() -> CheckResult:
    """بررسی فایل config."""
    from persian_devkit.utils.config_utils import CONFIG_FILE

    if not CONFIG_FILE.exists():
        return CheckResult(
            "Config file",
            "warn",
            f"وجود ندارد: {CONFIG_FILE}",
            "pdev config init",
        )
    try:
        from persian_devkit.utils.config_utils import load_config

        load_config()
        return CheckResult("Config file", "ok", f"معتبر: {CONFIG_FILE}")
    except Exception as exc:
        return CheckResult(
            "Config file",
            "fail",
            f"خراب است: {exc}",
            "pdev config reset",
        )


def _check_plugins_dir() -> CheckResult:
    """بررسی پوشهٔ پلاگین‌ها."""
    from persian_devkit.utils.plugin_utils import PLUGINS_DIR, discover_plugins

    if not PLUGINS_DIR.exists():
        return CheckResult(
            "Plugins dir",
            "warn",
            "وجود ندارد (اختیاری)",
            "pdev plugin init",
        )
    plugins = discover_plugins()
    return CheckResult(
        "Plugins dir",
        "ok",
        f"{len(plugins)} پلاگین نصب‌شده",
    )


def _check_write_permissions() -> CheckResult:
    """بررسی دسترسی نوشتن در پوشهٔ config."""
    from persian_devkit.utils.config_utils import CONFIG_DIR

    try:
        CONFIG_DIR.mkdir(parents=True, exist_ok=True)
        test_file = CONFIG_DIR / ".write_test"
        test_file.write_text("test", encoding="utf-8")
        test_file.unlink()
        return CheckResult(
            "Write permissions", "ok", f"می‌توان در {CONFIG_DIR} نوشت"
        )
    except (OSError, PermissionError) as exc:
        return CheckResult(
            "Write permissions",
            "fail",
            f"نمی‌توان در {CONFIG_DIR} نوشت: {exc}",
            "مجوزهای پوشه را چک کن",
        )


def _check_encoding() -> CheckResult:
    """بررسی encoding روی ویندوز."""
    if sys.platform == "win32":
        try:
            stdout_enc = sys.stdout.encoding or "unknown"
            if "utf" in stdout_enc.lower():
                return CheckResult("Encoding", "ok", f"UTF-8 فعال ({stdout_enc})")
            return CheckResult(
                "Encoding",
                "warn",
                f"کدپیج فعلی: {stdout_enc}",
                "chcp 65001 را قبل از اجرا بزن",
            )
        except Exception as exc:
            return CheckResult("Encoding", "warn", f"خطا: {exc}")
    return CheckResult("Encoding", "ok", "UTF-8 پیش‌فرض")


def _check_platform() -> CheckResult:
    """بررسی سیستم‌عامل."""
    os_name = platform.system()
    release = platform.release()
    return CheckResult("Platform", "ok", f"{os_name} {release}")


def run_all_checks() -> list[CheckResult]:
    """اجرای همهٔ بررسی‌ها."""
    results: list[CheckResult] = [
        _check_python_version(),
        _check_package_version(),
        _check_platform(),
        _check_encoding(),
    ]

    # وابستگی‌های اجباری
    for name in _REQUIRED:
        results.append(_check_dependency(name, required=True))

    # وابستگی‌های اختیاری
    for name, purpose in _OPTIONAL.items():
        results.append(_check_dependency(name, required=False, purpose=purpose))

    # config و plugins
    results.append(_check_config())
    results.append(_check_plugins_dir())
    results.append(_check_write_permissions())

    return results


def summary(results: list[CheckResult]) -> dict:
    """خلاصهٔ نتایج."""
    ok = sum(1 for r in results if r.status == "ok")
    warn = sum(1 for r in results if r.status == "warn")
    fail = sum(1 for r in results if r.status == "fail")
    return {"ok": ok, "warn": warn, "fail": fail, "total": len(results)}