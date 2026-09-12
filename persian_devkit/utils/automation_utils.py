"""توابع کمکی خودکارسازی: اجرای دستور، پایش، cron."""
from __future__ import annotations

import subprocess
import sys
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable, Optional


#command


@dataclass
class RunResult:
    """نتیجهٔ اجرای یک دستور."""

    command: str
    returncode: int
    stdout: str = ""
    stderr: str = ""
    duration: float = 0.0
    timed_out: bool = False

    @property
    def success(self) -> bool:
        return self.returncode == 0 and not self.timed_out


def run_command(
    command: str,
    timeout: Optional[float] = None,
    cwd: Optional[Path] = None,
    shell: bool = True,
) -> RunResult:
    """اجرای یک دستور shell و برگرداندن نتیجه."""
    start = time.perf_counter()
    try:
        result = subprocess.run(
            command,
            shell=shell,
            capture_output=True,
            text=True,
            timeout=timeout,
            cwd=str(cwd) if cwd else None,
            encoding="utf-8",
            errors="replace",
        )
        duration = time.perf_counter() - start
        return RunResult(
            command=command,
            returncode=result.returncode,
            stdout=result.stdout,
            stderr=result.stderr,
            duration=duration,
        )
    except subprocess.TimeoutExpired as exc:
        duration = time.perf_counter() - start
        return RunResult(
            command=command,
            returncode=-1,
            stdout=(exc.stdout or "") if isinstance(exc.stdout, str) else "",
            stderr=f"timeout پس از {timeout} ثانیه",
            duration=duration,
            timed_out=True,
        )
    except FileNotFoundError as exc:
        duration = time.perf_counter() - start
        return RunResult(
            command=command,
            returncode=-2,
            stderr=f"دستور یافت نشد: {exc}",
            duration=duration,
        )


#repeat


def repeat_command(
    command: str,
    times: int = 1,
    interval: float = 0.0,
    timeout: Optional[float] = None,
    stop_on_error: bool = False,
    on_iteration: Optional[Callable[[int, RunResult], None]] = None,
) -> list[RunResult]:
    """اجرای یک دستور چند بار با فاصلهٔ زمانی."""
    if times < 1:
        raise ValueError("times باید حداقل ۱ باشد")

    results: list[RunResult] = []
    for i in range(1, times + 1):
        result = run_command(command, timeout=timeout)
        results.append(result)
        if on_iteration:
            on_iteration(i, result)
        if stop_on_error and not result.success:
            break
        if i < times and interval > 0:
            time.sleep(interval)
    return results


#batch


@dataclass
class BatchStep:
    """یک مرحله از یک batch."""

    command: str
    stop_on_error: bool = True
    timeout: Optional[float] = None


def parse_batch_file(path: Path) -> list[BatchStep]:
    """تجزیهٔ فایل batch.

    هر خط یک دستور. خطوط خالی و # کامنت نادیده گرفته می‌شوند.
    خطی که با `!` شروع شود، خطا را نادیده می‌گیرد (stop_on_error=False).
    """
    if not path.exists():
        raise ValueError(f"فایل یافت نشد: {path}")

    steps: list[BatchStep] = []
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        ignore_error = False
        if line.startswith("!"):
            ignore_error = True
            line = line[1:].strip()
        if line:
            steps.append(BatchStep(command=line, stop_on_error=not ignore_error))
    return steps


def run_batch(
    steps: list[BatchStep],
    cwd: Optional[Path] = None,
    on_step: Optional[Callable[[int, BatchStep, RunResult], None]] = None,
) -> list[RunResult]:
    """اجرای یک batch مرحله‌به‌مرحله."""
    results: list[RunResult] = []
    for i, step in enumerate(steps, 1):
        result = run_command(step.command, timeout=step.timeout, cwd=cwd)
        results.append(result)
        if on_step:
            on_step(i, step, result)
        if not result.success and step.stop_on_error:
            break
    return results


#watch


def watch_path(
    path: Path,
    command: str,
    interval: float = 1.0,
    max_iterations: Optional[int] = None,
    timeout: Optional[float] = None,
    on_change: Optional[Callable[[Path, RunResult], None]] = None,
) -> None:
    """پایش یک فایل یا پوشه و اجرای دستور هنگام تغییر.

    با polling هر ``interval`` ثانیه تغییرات را بررسی می‌کند.
    """
    if not path.exists():
        raise ValueError(f"مسیر یافت نشد: {path}")

    if path.is_file():
        def get_mtime() -> float:
            try:
                return path.stat().st_mtime
            except OSError:
                return 0.0
    else:
        def get_mtime() -> float:
            try:
                return max(
                    (p.stat().st_mtime for p in path.rglob("*") if p.is_file()),
                    default=0.0,
                )
            except OSError:
                return 0.0

    last = get_mtime()
    iterations = 0
    while True:
        time.sleep(interval)
        current = get_mtime()
        if current != last:
            last = current
            result = run_command(command, timeout=timeout)
            if on_change:
                on_change(path, result)
        iterations += 1
        if max_iterations is not None and iterations >= max_iterations:
            break


#cron


_CRON_MONTHS = [
    "ژانویه", "فوریه", "مارس", "آپریل", "مه", "ژوئن",
    "جولای", "آگوست", "سپتامبر", "اکتبر", "نوامبر", "دسامبر",
]

_CRON_WEEKDAYS = [
    "یکشنبه", "دوشنبه", "سه‌شنبه", "چهارشنبه", "پنجشنبه", "جمعه", "شنبه",
]

_CRON_PRESETS = {
    "@yearly": "0 0 1 1 *",
    "@annually": "0 0 1 1 *",
    "@monthly": "0 0 1 * *",
    "@weekly": "0 0 * * 0",
    "@daily": "0 0 * * *",
    "@midnight": "0 0 * * *",
    "@hourly": "0 * * * *",
}


def parse_cron(expr: str) -> dict:
    """تجزیهٔ عبارت cron (۵ فیلد) یا preset (@daily و ...).

    خروجی: دیکشنری شامل دقیقه، ساعت، روز، ماه، روز هفته.
    """
    expr = expr.strip()
    if expr.startswith("@"):
        if expr not in _CRON_PRESETS:
            raise ValueError(f"preset ناشناخته: {expr}")
        expr = _CRON_PRESETS[expr]

    parts = expr.split()
    if len(parts) != 5:
        raise ValueError(
            f"عبارت cron باید ۵ فیلد داشته باشد: دقیقه ساعت روز ماه روزهفته (دریافت شد: {len(parts)})"
        )

    minute, hour, day, month, weekday = parts

    def _field(spec: str, lo: int, hi: int, name: str) -> list[int]:
        """تجزیهٔ یک فیلد cron به لیست اعداد."""
        values: set[int] = set()

        # پشتیبانی از */n و a-b/n و a,b,c
        for chunk in spec.split(","):
            chunk = chunk.strip()
            step = 1
            if "/" in chunk:
                chunk, step_s = chunk.split("/", 1)
                try:
                    step = int(step_s)
                except ValueError as exc:
                    raise ValueError(f"گام نامعتبر در {name}: {step_s}") from exc
                if step < 1:
                    raise ValueError(f"گام باید مثبت باشد در {name}")

            if chunk == "*":
                start, end = lo, hi
            elif "-" in chunk:
                a_s, b_s = chunk.split("-", 1)
                try:
                    start, end = int(a_s), int(b_s)
                except ValueError as exc:
                    raise ValueError(f"بازهٔ نامعتبر در {name}: {chunk}") from exc
            else:
                try:
                    start = end = int(chunk)
                except ValueError as exc:
                    raise ValueError(f"مقدار نامعتبر در {name}: {chunk}") from exc

            if start < lo or end > hi:
                raise ValueError(f"مقدار خارج از بازهٔ {lo}-{hi} در {name}: {chunk}")

            values.update(range(start, end + 1, step))
        return sorted(values)

    return {
        "minute": _field(minute, 0, 59, "دقیقه"),
        "hour": _field(hour, 0, 23, "ساعت"),
        "day": _field(day, 1, 31, "روز"),
        "month": _field(month, 1, 12, "ماه"),
        "weekday": _field(weekday, 0, 6, "روز هفته"),
    }


def explain_cron(expr: str) -> str:
    """توضیح فارسی یک عبارت cron."""
    parsed = parse_cron(expr)

    def _fmt_list(values: list[int], total: int) -> str:
        if len(values) == total:
            return "هر"
        if len(values) == 1:
            return str(values[0])
        return ", ".join(str(v) for v in values)

    minute = _fmt_list(parsed["minute"], 60)
    hour = _fmt_list(parsed["hour"], 24)
    day = _fmt_list(parsed["day"], 31)
    month = _fmt_list(parsed["month"], 12)
    weekday_vals = parsed["weekday"]

    parts: list[str] = []

    # زمان
    if minute == "هر" and hour == "هر":
        parts.append("هر دقیقه")
    elif hour == "هر":
        parts.append(f"در دقیقهٔ {minute} هر ساعت")
    else:
        parts.append(f"در ساعت {hour}:{minute if minute != 'هر' else '00'}")

    # روز هفته
    if len(weekday_vals) < 7:
        days = [_CRON_WEEKDAYS[v] for v in weekday_vals]
        parts.append("روزهای " + ", ".join(days))

    # روز ماه
    if len(parsed["day"]) < 31:
        parts.append(f"روز {day} ماه")

    # ماه
    if len(parsed["month"]) < 12:
        months = [_CRON_MONTHS[m - 1] for m in parsed["month"]]
        parts.append("ماه‌های " + ", ".join(months))

    return " ".join(parts)