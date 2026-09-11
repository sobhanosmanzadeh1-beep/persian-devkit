"""ثبت تمام زیرفرمان‌ها روی اپ اصلی Typer."""
from __future__ import annotations

import typer

from persian_devkit.commands import (
    base64_cmd, color_cmd, csv_cmd, date_cmd, env_cmd, gitignore_cmd,
    hash_cmd, image_cmd, jq_cmd, json_cmd, license_cmd, lorem_cmd,
    name_cmd, number_cmd, password_cmd, qrcode_cmd, random_cmd,
    scaffold_cmd, template_cmd, text_cmd, time_cmd, toml_cmd,
    url_cmd, uuid_cmd, yaml_cmd,
)
from persian_devkit.commands.jq_cmd import jq_command
from persian_devkit.commands.scaffold_cmd import scaffold_command
from persian_devkit.commands.template_cmd import template_command


def register_commands(app: typer.Typer) -> None:
    """همهٔ زیرفرمان‌ها را به اپ اضافه می‌کند."""
    # فارسی و عمومی (Batch 1-2)
    app.add_typer(date_cmd.app, name="date", help="📅 تاریخ.")
    app.add_typer(number_cmd.app, name="number", help="🔢 اعداد.")
    app.add_typer(text_cmd.app, name="text", help="✍️  متن.")
    app.add_typer(uuid_cmd.app, name="uuid", help="🆔 UUID.")
    app.add_typer(json_cmd.app, name="json", help="🗂️  JSON.")
    app.add_typer(base64_cmd.app, name="base64", help="🔐 Base64.")
    app.add_typer(hash_cmd.app, name="hash", help="🧮 هش.")
    app.add_typer(password_cmd.app, name="password", help="🔑 رمز.")
    app.add_typer(random_cmd.app, name="random", help="🎲 تصادفی.")

    # شبکه و وب (Batch 3)
    app.add_typer(url_cmd.app, name="url", help="🔗 URL.")
    app.add_typer(time_cmd.app, name="time", help="⏱  زمان.")

    # بصری (Batch 3)
    app.add_typer(color_cmd.app, name="color", help="🎨 رنگ.")
    app.add_typer(image_cmd.app, name="image", help="🖼  تصویر.")
    app.command(name="qrcode", help="📱 QR Code.")(qrcode_cmd.qrcode_command)

    # داده (Batch 4-5)
    app.add_typer(yaml_cmd.app, name="yaml", help="📄 YAML.")
    app.add_typer(toml_cmd.app, name="toml", help="⚙️  TOML.")
    app.add_typer(csv_cmd.app, name="csv", help="📊 CSV.")
    app.add_typer(env_cmd.app, name="env", help="🔐 .env.")
    app.command(name="jq", help="🔍 کوئری JSON.")(jq_command)

    # دادهٔ نمونه (Batch 5)
    app.add_typer(lorem_cmd.app, name="lorem", help="📝 متن نمونهٔ فارسی.")
    app.add_typer(name_cmd.app, name="name", help="👤 نام نمونهٔ فارسی.")

    # ابزار پروژه (Batch 6)
    app.add_typer(license_cmd.app, name="license", help="📜 لایسنس.")
    app.add_typer(gitignore_cmd.app, name="gitignore", help="🚫 .gitignore.")
    app.command(name="scaffold", help="🏗  ساخت پروژه از قالب.")(scaffold_command)
    app.command(name="template", help="📋 رندر قالب متنی.")(template_command)