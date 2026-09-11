"""نقطهٔ ورود اصلی ابزار pdev."""
from __future__ import annotations

import sys

# اصلاح encoding در ویندوز
if sys.platform == "win32":
    for _stream_name in ("stdin", "stdout", "stderr"):
        _stream = getattr(sys, _stream_name, None)
        if _stream is not None and hasattr(_stream, "reconfigure"):
            try:
                _stream.reconfigure(encoding="utf-8")
            except Exception:
                pass

import typer
from persian_devkit import __version__
from persian_devkit.cli import register_commands

app = typer.Typer(
    name="pdev",
    help="جعبه‌ابزار خط فرمان برای توسعه‌دهندگان فارسی‌زبان.",
    no_args_is_help=True,
    add_completion=True,
    rich_markup_mode="rich",
)


def _version_callback(value: bool) -> None:
    """نمایش نسخه و خروج فوری."""
    if value:
        typer.echo(f"persian-devkit {__version__}")
        raise typer.Exit()


@app.callback()
def main_callback(
    ctx: typer.Context,
    version: bool = typer.Option(
        False,
        "--version",
        "-V",
        help="نمایش نسخهٔ ابزار و خروج.",
        callback=_version_callback,
        is_eager=True,
    ),
    verbose: bool = typer.Option(
        False, "--verbose", "-v", help="نمایش جزئیات بیشتر در خروجی."
    ),
    quiet: bool = typer.Option(
        False, "--quiet", "-q", help="کاهش پیام‌های اضافی (فقط نتیجه)."
    ),
) -> None:
    """گزینه‌های سراسری pdev."""
    ctx.obj = {"verbose": verbose, "quiet": quiet}


# ثبت زیرفرمان‌ها
register_commands(app)


if __name__ == "__main__":  # pragma: no cover
    app()