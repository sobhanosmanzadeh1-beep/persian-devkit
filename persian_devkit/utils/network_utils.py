"""توابع کمکی شبکه: IP، پورت، ping."""
from __future__ import annotations

import socket
import subprocess
import sys
from typing import Optional


def get_local_ip() -> str:
    """IP محلی دستگاه (روی شبکهٔ فعلی)."""
    try:
        # اتصال dummy به یک سرور عمومی بدون ارسال داده
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.settimeout(0.5)
            s.connect(("8.8.8.8", 80))
            return s.getsockname()[0]
    except OSError:
        try:
            return socket.gethostbyname(socket.gethostname())
        except OSError:
            return "127.0.0.1"


def get_hostname() -> str:
    """نام هاست دستگاه."""
    try:
        return socket.gethostname()
    except OSError:
        return "unknown"


def get_fqdn() -> str:
    """نام کامل (FQDN) دستگاه."""
    try:
        return socket.getfqdn()
    except OSError:
        return "unknown"


def get_public_ip() -> Optional[str]:
    """IP عمومی با استفاده از یک سرویس آنلاین."""
    import httpx

    services = [
        "https://api.ipify.org",
        "https://ifconfig.me/ip",
        "https://icanhazip.com",
    ]
    for service in services:
        try:
            r = httpx.get(service, timeout=5.0)
            if r.status_code == 200:
                return r.text.strip()
        except Exception:
            continue
    return None


def is_port_open(host: str, port: int, timeout: float = 2.0) -> bool:
    """بررسی باز بودن یک پورت TCP."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(timeout)
        try:
            s.connect((host, port))
            return True
        except (socket.timeout, ConnectionRefusedError, OSError):
            return False


def resolve_hostname(host: str) -> str:
    """تبدیل نام دامنه به IP."""
    try:
        return socket.gethostbyname(host)
    except socket.gaierror as exc:
        raise ValueError(f"دامنه پیدا نشد: {host}") from exc


def ping_host(host: str, count: int = 4, timeout: int = 5) -> dict:
    """ارسال ping و برگرداندن نتیجه."""
    if sys.platform == "win32":
        cmd = ["ping", "-n", str(count), "-w", str(timeout * 1000), host]
    else:
        cmd = ["ping", "-c", str(count), "-W", str(timeout), host]

    try:
        result = subprocess.run(
            cmd, capture_output=True, text=True, timeout=count * timeout + 5
        )
    except subprocess.TimeoutExpired:
        return {"success": False, "error": "timeout", "output": ""}
    except FileNotFoundError:
        return {"success": False, "error": "ping-not-found", "output": ""}

    return {
        "success": result.returncode == 0,
        "output": result.stdout,
        "error": result.stderr.strip() if result.returncode != 0 else "",
    }
