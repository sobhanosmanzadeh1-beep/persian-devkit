"""توابع کمکی مشترک برای YAML، TOML، CSV و ENV."""
from __future__ import annotations

import csv
import io
import json
import sys
from pathlib import Path
from typing import Any, Optional

if sys.version_info >= (3, 11):
    import tomllib
else:  # pragma: no cover
    import tomli as tomllib

import tomli_w
import yaml


#IO


def read_text(path: Path) -> str:
    """فایل متنی را با UTF-8 می‌خواند."""
    return path.read_text(encoding="utf-8")


def write_text(path: Path, text: str) -> None:
    """نوشتن متن در فایل با UTF-8."""
    path.write_text(text, encoding="utf-8")


#YAML


def parse_yaml(text: str) -> Any:
    """پارس YAML به شیء پایتون."""
    try:
        return yaml.safe_load(text)
    except yaml.YAMLError as exc:
        raise ValueError(f"YAML نامعتبر: {exc}") from exc


def dump_yaml(data: Any) -> str:
    """تبدیل شیء پایتون به YAML."""
    return yaml.safe_dump(
        data, allow_unicode=True, sort_keys=False, default_flow_style=False
    )


#TOML


def parse_toml(text: str) -> dict:
    """پارس TOML به دیکشنری."""
    try:
        return tomllib.loads(text)
    except tomllib.TOMLDecodeError as exc:
        raise ValueError(f"TOML نامعتبر: {exc}") from exc


def dump_toml(data: dict) -> str:
    """تبدیل دیکشنری به TOML."""
    try:
        return tomli_w.dumps(data)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"خطا در تولید TOML: {exc}") from exc


#JSON


def parse_json(text: str) -> Any:
    """پارس JSON با پیام خطای فارسی."""
    try:
        return json.loads(text)
    except json.JSONDecodeError as exc:
        raise ValueError(f"JSON نامعتبر: {exc}") from exc


def dump_json(data: Any, indent: int = 2, ensure_ascii: bool = False) -> str:
    """تبدیل شیء به JSON با پشتیبانی یونیکد."""
    return json.dumps(data, ensure_ascii=ensure_ascii, indent=indent)


#CSV


def read_csv(path: Path, delimiter: str = ",") -> tuple[list[str], list[dict]]:
    """فایل CSV را می‌خواند و (هدر، ردیف‌ها) برمی‌گرداند.

    هر ردیف یک دیکشنری با کلیدهای هدر است.
    """
    text = read_text(path)
    reader = csv.DictReader(io.StringIO(text), delimiter=delimiter)
    if reader.fieldnames is None:
        return [], []
    headers = list(reader.fieldnames)
    rows = [dict(r) for r in reader]
    return headers, rows


def write_csv(path: Path, headers: list[str], rows: list[dict], delimiter: str = ",") -> None:
    """نوشتن ردیف‌ها در فایل CSV."""
    buf = io.StringIO()
    writer = csv.DictWriter(buf, fieldnames=headers, delimiter=delimiter)
    writer.writeheader()
    for row in rows:
        writer.writerow(row)
    write_text(path, buf.getvalue())


#ENV


def parse_env(text: str) -> dict[str, str]:
    """پارس محتوای .env به دیکشنری.

    خطوط با # به‌عنوان کامنت نادیده گرفته می‌شوند.
    مقادیر داخل "..." یا '...' بدون کوتیشن برمی‌گردند.
    """
    result: dict[str, str] = {}
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        if "=" not in line:
            continue
        key, _, value = line.partition("=")
        key = key.strip()
        value = value.strip()
        if len(value) >= 2 and value[0] == value[-1] and value[0] in ("'", '"'):
            value = value[1:-1]
        if key:
            result[key] = value
    return result


def dump_env(data: dict[str, str]) -> str:
    """تبدیل دیکشنری به محتوای .env."""
    lines: list[str] = []
    for key, value in data.items():
        if any(c in value for c in (" ", "#", "'", '"')):
            value = f'"{value}"'
        lines.append(f"{key}={value}")
    return "\n".join(lines) + "\n"