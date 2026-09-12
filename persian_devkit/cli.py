"""ثبت تمام زیرفرمان‌ها روی اپ اصلی Typer."""
from __future__ import annotations

import typer
from persian_devkit.commands import (
    automation_cmd, base64_cmd, calendar_cmd, color_cmd, count_cmd,
    csv_cmd, csvquery_cmd, date_cmd, dns_cmd, env_cmd, extract_cmd,
    fa_cmd, frequency_cmd, gitignore_cmd, hash_cmd, hijri_cmd,
    http_cmd, image_cmd, ip_cmd, jq_cmd, json_cmd, license_cmd,
    lorem_cmd, name_cmd, number_cmd, numerals_cmd, password_cmd,
    ping_cmd, port_cmd, qrcode_cmd, random_cmd, scaffold_cmd,
    security_cmd, sort_cmd, sqlite_cmd, sys_cmd, template_cmd,
    text_cmd, time_cmd, toml_cmd, translit_cmd, uniq_cmd, url_cmd,
    uuid_cmd, yaml_cmd,
)
from persian_devkit.commands.jq_cmd import jq_command
from persian_devkit.commands.scaffold_cmd import scaffold_command
from persian_devkit.commands.template_cmd import template_command


def register_commands(app: typer.Typer) -> None:
    """همهٔ زیرفرمان‌ها را به اپ اضافه می‌کند."""
    # سیستم (Batch 10)
    app.add_typer(sys_cmd.app, name="sys", help=" اطلاعات سیستم.")
    # تاریخ و زمان
    app.add_typer(date_cmd.app, name="date", help=" تاریخ شمسی/میلادی.")
    app.add_typer(hijri_cmd.app, name="hijri", help=" تاریخ قمری.")
    app.add_typer(calendar_cmd.app, name="calendar", help=" تقویم ماهانه.")
    app.add_typer(time_cmd.app, name="time", help="  timestamp و مدت زمان.")

    # متن
    app.add_typer(text_cmd.app, name="text", help="  پردازش متن فارسی.")
    app.add_typer(translit_cmd.app, name="transliterate", help=" فارسی ↔ فینگلیش.")
    app.add_typer(sort_cmd.app, name="sort", help=" مرتب‌سازی با الفبای فارسی.")

    # فارسی پیشرفته (Batch 13)
    app.add_typer(fa_cmd.app, name="fa", help="🇮🇷 ابزارهای پیشرفتهٔ فارسی.")

    # متن پیشرفته (Batch 9)
    app.add_typer(count_cmd.app, name="count", help=" شمارش خط/کلمه/کاراکتر.")
    app.add_typer(frequency_cmd.app, name="frequency", help=" کلمات پرتکرار.")
    app.add_typer(uniq_cmd.app, name="uniq", help=" حذف تکراری‌ها.")
    app.add_typer(extract_cmd.app, name="extract", help=" استخراج ایمیل/URL/عدد.")

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

    # دیتابیس (Batch 12)
    app.add_typer(sqlite_cmd.app, name="sqlite", help="  کار با SQLite.")
    app.add_typer(csvquery_cmd.app, name="csv-query", help=" کوئری SQL روی CSV.")

    # وب
    app.add_typer(url_cmd.app, name="url", help=" URL.")

    # شبکه (Batch 8)
    app.add_typer(ip_cmd.app, name="ip", help=" IP و اطلاعات شبکه.")
    app.add_typer(dns_cmd.app, name="dns", help=" جستجوی DNS.")
    app.add_typer(port_cmd.app, name="port", help=" بررسی پورت.")
    app.add_typer(http_cmd.app, name="http", help=" درخواست HTTP.")
    app.add_typer(ping_cmd.app, name="ping", help=" ping هاست.")

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

    # خودکارسازی (Batch 14)
    app.add_typer(automation_cmd.app, name="auto", help=" خودکارسازی: repeat, batch, watch.")

    # امنیت (Batch 11)
    app.add_typer(security_cmd.app, name="security", help=" امنیت: JWT، رمز، گواهی.")