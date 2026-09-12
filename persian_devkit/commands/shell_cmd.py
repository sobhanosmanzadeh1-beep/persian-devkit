"""دستور pdev shell — حالت تعاملی (REPL)."""
from __future__ import annotations

import os
import shlex
import subprocess
import sys

import typer
from rich.console import Console
from rich.panel import Panel

from persian_devkit.utils.config_utils import get_value, load_config
from persian_devkit.utils.plugin_utils import discover_plugins

console = Console()

_BANNER = """ persian-devkit v2.0.0 — حالت تعاملی
دستورات داخلی: :help، :exit، :clear، :config، :plugins
برای دیدن راهنما: :help"""

_HELP = """[bold]دستورات داخلی:[/bold]
  [cyan]:help[/cyan] (:h)      نمایش راهنما
  [cyan]:exit[/cyan] (:q)      خروج
  [cyan]:clear[/cyan] (:c)     پاک‌سازی صفحه
  [cyan]:config[/cyan]          نمایش تنظیمات
  [cyan]:plugins[/cyan]         لیست پلاگین‌ها
  [cyan]!<cmd>[/cyan]           اجرای دستور سیستم

[bold]نمونه:[/bold]
  date now
  number words 1234
  text slug "سلام دنیا"
  hash text hello"""


def _clear_screen() -> None:
    os.system("cls" if sys.platform == "win32" else "clear")


def _run_pdev(line: str) -> int:
    """اجرای یک دستور pdev در subprocess."""
    try:
        args = shlex.split(line)
    except ValueError as exc:
        console.print(f"[red]خطای تجزیه:[/red] {exc}")
        return 1
    if not args:
        return 0
    cmd = [sys.executable, "-m", "persian_devkit"] + args
    try:
        return subprocess.call(cmd)
    except KeyboardInterrupt:
        console.print("\n[yellow]^C[/yellow]")
        return 130


def _run_shell(cmd: str) -> int:
    """اجرای دستور سیستم."""
    try:
        return subprocess.call(cmd, shell=True)
    except KeyboardInterrupt:
        console.print("\n[yellow]^C[/yellow]")
        return 130


def shell_command() -> None:
    """شروع حالت تعاملی pdev (REPL).

    با Ctrl+D یا :exit خارج می‌شود.
    """
    if get_value("shell.banner", True):
        console.print(Panel(_BANNER, style="cyan", title="✨ pdev shell", expand=False))

    while True:
        try:
            line = input("pdev> ").strip()
        except (EOFError, KeyboardInterrupt):
            console.print("\n[dim]خداحافظ![/dim]")
            break

        if not line:
            continue

        # دستورات داخلی
        if line in (":exit", ":q", ":quit"):
            console.print("[dim]خداحافظ![/dim]")
            break
        if line in (":help", ":h", "?"):
            console.print(_HELP)
            continue
        if line in (":clear", ":c"):
            _clear_screen()
            continue
        if line == ":config":
            console.print_json(data=load_config())
            continue
        if line == ":plugins":
            plugins = discover_plugins()
            if not plugins:
                console.print("[yellow]هیچ پلاگینی نصب نیست.[/yellow]")
                continue
            for p in plugins:
                console.print(f"  🔌 [bold]{p.name}[/bold]  [dim]{p.description}[/dim]")
            continue
        if line.startswith("!"):
            _run_shell(line[1:].strip())
            continue
        if line.startswith(":"):
            console.print(f"[yellow]دستور ناشناخته:[/yellow] {line}")
            continue

        # اجرا به‌عنوان دستور pdev
        _run_pdev(line)