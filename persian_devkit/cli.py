"""ثبت تمام زیرفرمان‌ها روی اپ اصلی Typer."""
from __future__ import annotations

import typer

from persian_devkit.commands import (
    base64_cmd, calendar_cmd, color_cmd, csv_cmd, date_cmd, env_cmd,
    gitignore_cmd, hash_cmd, hijri_cmd, image_cmd, jq_cmd, json_cmd,
    license_cmd, lorem_cmd, name_cmd, number_cmd, numerals_cmd,
    password_cmd, qrcode_cmd, random_cmd, scaffold_cmd, sort_cmd,
    template_cmd, text_cmd, time_cmd, toml_cmd, translit_cmd,
    url_cmd, uuid_cmd, yaml_cmd,
)
from persian_devkit.commands.jq_cmd import jq_command
from persian_devkit.commands.scaffold_cmd import scaffold_command
from persian_devkit.commands.template_cmd import template_command


def register_commands(app: typer.Typer) -> None:
    """همهٔ زیرفرمان‌ها را به اپ اضافه می‌کند."""
    # تاریخ و زمان
    app.add_typer(date_cmd.app, name="date", help=" تاریخ شمسی/میلادی.")
    app.add_typer(hijri_cmd.app, name="hijri", help=" تاریخ قمری.")
    app.add_typer(calendar_cmd.app, name="calendar", help=" تقویم ماهانه.")
    app.add_typer(time_cmd.app, name="time", help="  timestamp و مدت زمان.")

    # متن
    app.add_typer(text_cmd.app, name="text", help="  پردازش متن فارسی.")
    app.add_typer(translit_cmd.app, name="transliterate", help=" فارسی ↔ فینگلیش.")
    app.add_typer(sort_cmd.app, name="sort", help=" مرتب‌سازی با الفبای فارسی.")

    # اعداد
    app.add_typer(number_cmd.app, name="number", help=" اعداد.")
    app.add_typer(numerals_cmd.app, name="numerals", help=" اعداد ترتیبی.")

    # کریپتو
    app.add_typer(base64_cmd.app, name="base64", help=" Base64.")
    app.add_typer(hash_cmd.app, name="hash", help=" هش.")
    app.add_typer(password_cmd.app, name="password", help=" رمز.")
    app.add_typer(random_cmd.app, name="random", help=" تصادفی.")
    app.add_typer(uuid_cmd.app, name="uuid", help=" UUID.")

    # داده
    app.add_typer(json_cmd.app, name="json", help="  JSON.")
    app.add_typer(yaml_cmd.app, name="yaml", help=" YAML.")
    app.add_typer(toml_cmd.app, name="toml", help="  TOML.")
    app.add_typer(csv_cmd.app, name="csv", help=" CSV.")
    app.add_typer(env_cmd.app, name="env", help=" .env.")
    app.command(name="jq", help=" کوئری JSON.")(jq_command)

    # وب
    app.add_typer(url_cmd.app, name="url", help=" URL.")

    # بصری
    app.add_typer(color_cmd.app, name="color", help=" رنگ.")
    app.add_typer(image_cmd.app, name="image", help="  تصویر.")
    app.command(name="qrcode", help=" QR Code.")(qrcode_cmd.qrcode_command)

    # نمونه
    app.add_typer(lorem_cmd.app, name="lorem", help=" متن نمونه.")
    app.add_typer(name_cmd.app, name="name", help=" نام نمونه.")

    # ابزار پروژه
    app.add_typer(license_cmd.app, name="license", help=" لایسنس.")
    app.add_typer(gitignore_cmd.app, name="gitignore", help=" .gitignore.")
    app.command(name="scaffold", help="  ساخت پروژه از قالب.")(scaffold_command)
    app.command(name="template", help=" رندر قالب.")(template_command)