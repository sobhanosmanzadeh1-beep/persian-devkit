"""توابع کمکی اطلاعات سیستم."""
from __future__ import annotations

import platform
import shutil
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional

try:
    import psutil  # type: ignore
    _HAS_PSUTIL = True
except ImportError:
    _HAS_PSUTIL = False


def _require_psutil() -> None:
    """اگر psutil نصب نباشد، خطا می‌دهد."""
    if not _HAS_PSUTIL:
        raise RuntimeError(
            "برای این قابلیت باید psutil نصب باشد: pip install psutil"
        )


def python_info() -> dict:
    """اطلاعات پایتون و سیستم."""
    return {
        "python_version": sys.version.split()[0],
        "python_impl": platform.python_implementation(),
        "executable": sys.executable,
        "platform": platform.platform(),
        "system": platform.system(),
        "release": platform.release(),
        "machine": platform.machine(),
        "processor": platform.processor(),
        "architecture": platform.architecture()[0],
    }


def disk_info(path: Optional[Path] = None) -> dict:
    """اطلاعات دیسک."""
    target = str(path) if path else str(Path.home().anchor or "/")
    try:
        usage = shutil.disk_usage(target)
        return {
            "path": target,
            "total": usage.total,
            "used": usage.used,
            "free": usage.free,
            "percent": round(usage.used / usage.total * 100, 1) if usage.total else 0.0,
        }
    except (OSError, PermissionError) as exc:
        raise RuntimeError(f"خطا در خواندن دیسک {target}: {exc}") from exc


def memory_info() -> dict:
    """اطلاعات حافظه (RAM)."""
    _require_psutil()
    vm = psutil.virtual_memory()
    sm = psutil.swap_memory()
    return {
        "total": vm.total,
        "available": vm.available,
        "used": vm.used,
        "percent": vm.percent,
        "swap_total": sm.total,
        "swap_used": sm.used,
        "swap_percent": sm.percent,
    }


def cpu_info() -> dict:
    """اطلاعات پردازنده."""
    _require_psutil()
    freq = psutil.cpu_freq()
    return {
        "physical_cores": psutil.cpu_count(logical=False),
        "logical_cores": psutil.cpu_count(logical=True),
        "percent": psutil.cpu_percent(interval=0.5),
        "freq_current": freq.current if freq else None,
        "freq_max": freq.max if freq else None,
    }


def uptime() -> timedelta:
    """مدت زمان روشن بودن سیستم."""
    _require_psutil()
    boot_time = psutil.boot_time()
    return datetime.now() - datetime.fromtimestamp(boot_time)


def format_bytes(n: int) -> str:
    """قالب‌بندی خوانا برای بایت."""
    value = float(n)
    for unit in ("B", "KB", "MB", "GB", "TB", "PB"):
        if value < 1024:
            return f"{value:.2f} {unit}"
        value /= 1024
    return f"{value:.2f} EB"


def top_processes(limit: int = 10, by: str = "cpu") -> list[dict]:
    """پرمصرف‌ترین پردازش‌ها."""
    _require_psutil()
    if by not in ("cpu", "memory"):
        raise ValueError(f"by باید cpu یا memory باشد: {by}")

    procs = []
    for p in psutil.process_iter(["pid", "name", "cpu_percent", "memory_percent"]):
        try:
            info = p.info
            procs.append(
                {
                    "pid": info["pid"],
                    "name": info["name"] or "?",
                    "cpu": round(info["cpu_percent"] or 0.0, 1),
                    "memory": round(info["memory_percent"] or 0.0, 1),
                }
            )
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue

    key = "cpu" if by == "cpu" else "memory"
    procs.sort(key=lambda x: x[key], reverse=True)
    return procs[:limit]