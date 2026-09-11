"""اطلاعات و تبدیل تصاویر."""
from __future__ import annotations

from pathlib import Path

from PIL import Image


def image_info(path: Path) -> dict:
    """اطلاعات فایل تصویری: فرمت، حالت، ابعاد، اندازه."""
    with Image.open(path) as img:
        return {
            "format": img.format or "unknown",
            "mode": img.mode,
            "width": img.width,
            "height": img.height,
            "size_bytes": path.stat().st_size,
        }


def resize_image(src: Path, dst: Path, width: int, height: int | None = None) -> None:
    """تغییر اندازهٔ تصویر (اگر height خالی باشد، نسبت حفظ می‌شود)."""
    with Image.open(src) as img:
        if height is None:
            ratio = width / img.width
            height = max(1, round(img.height * ratio))
        resized = img.resize((width, height), Image.LANCZOS)
        resized.save(dst)


def convert_image(src: Path, dst: Path, quality: int = 90) -> None:
    """تبدیل فرمت تصویر بر اساس پسوند مقصد."""
    with Image.open(src) as img:
        if dst.suffix.lower() in (".jpg", ".jpeg"):
            img.convert("RGB").save(dst, quality=quality)
        else:
            img.save(dst)