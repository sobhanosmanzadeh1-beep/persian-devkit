"""توابع کمکی کار با فایل‌های PDF."""
from __future__ import annotations

from pathlib import Path
from typing import Optional

from pypdf import PdfReader, PdfWriter


def _open(path: Path) -> PdfReader:
    """باز کردن فایل PDF با خطای فارسی."""
    if not path.exists():
        raise ValueError(f"فایل یافت نشد: {path}")
    try:
        return PdfReader(str(path))
    except Exception as exc:
        raise ValueError(f"خطا در باز کردن PDF: {exc}") from exc


def pdf_info(path: Path) -> dict:
    """اطلاعات فایل PDF."""
    reader = _open(path)
    meta = reader.metadata or {}

    def _get(key: str) -> str:
        val = meta.get(key)
        return str(val) if val else ""

    return {
        "pages": len(reader.pages),
        "encrypted": reader.is_encrypted,
        "title": _get("/Title"),
        "author": _get("/Author"),
        "subject": _get("/Subject"),
        "creator": _get("/Creator"),
        "producer": _get("/Producer"),
        "size_bytes": path.stat().st_size,
    }


def extract_text(path: Path, start: int = 1, end: Optional[int] = None) -> str:
    """استخراج متن از یک بازهٔ صفحه.

    شماره‌ها از ۱ شروع می‌شوند.
    """
    reader = _open(path)
    total = len(reader.pages)
    if start < 1 or start > total:
        raise ValueError(f"شمارهٔ صفحهٔ شروع نامعتبر (۱ تا {total})")
    if end is None:
        end = total
    if end < start or end > total:
        raise ValueError(f"شمارهٔ صفحهٔ پایان نامعتبر ({start} تا {total})")

    parts: list[str] = []
    for i in range(start - 1, end):
        try:
            text = reader.pages[i].extract_text() or ""
            parts.append(text)
        except Exception as exc:
            parts.append(f"[خطا در صفحهٔ {i + 1}: {exc}]")
    return "\n\n".join(parts)


def merge_pdfs(paths: list[Path], output: Path) -> int:
    """ادغام چند PDF در یک فایل. تعداد کل صفحات را برمی‌گرداند."""
    if len(paths) < 2:
        raise ValueError("حداقل دو فایل برای ادغام لازم است")

    writer = PdfWriter()
    total = 0
    for p in paths:
        if not p.exists():
            raise ValueError(f"فایل یافت نشد: {p}")
        try:
            reader = PdfReader(str(p))
            for page in reader.pages:
                writer.add_page(page)
                total += 1
        except Exception as exc:
            raise ValueError(f"خطا در خواندن {p}: {exc}") from exc

    with output.open("wb") as f:
        writer.write(f)
    return total


def split_pdf(
    path: Path, output: Path, start: int = 1, end: Optional[int] = None
) -> int:
    """استخراج بازه‌ای از صفحات به یک PDF جدید. تعداد صفحات خروجی را برمی‌گرداند."""
    reader = _open(path)
    total = len(reader.pages)
    if end is None:
        end = total
    if start < 1 or end > total or start > end:
        raise ValueError(f"بازهٔ نامعتبر ({start} تا {end}، کل {total})")

    writer = PdfWriter()
    for i in range(start - 1, end):
        writer.add_page(reader.pages[i])

    with output.open("wb") as f:
        writer.write(f)
    return end - start + 1