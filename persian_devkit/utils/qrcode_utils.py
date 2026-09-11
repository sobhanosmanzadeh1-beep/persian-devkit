"""تولید QR Code برای چاپ در ترمینال یا ذخیره در فایل."""
from __future__ import annotations

from pathlib import Path

import qrcode
from qrcode.constants import (
    ERROR_CORRECT_H,
    ERROR_CORRECT_L,
    ERROR_CORRECT_M,
    ERROR_CORRECT_Q,
)

_ERROR_LEVELS = {
    "L": ERROR_CORRECT_L,
    "M": ERROR_CORRECT_M,
    "Q": ERROR_CORRECT_Q,
    "H": ERROR_CORRECT_H,
}


def _make_qr(text: str, error: str = "M", box_size: int = 10, border: int = 2):
    """شیء QR را با تنظیمات داده‌شده می‌سازد."""
    if error not in _ERROR_LEVELS:
        raise ValueError(
            f"سطح تصحیح خطا نامعتبر: {error}. مجاز: L, M, Q, H"
        )
    qr = qrcode.QRCode(
        version=None,
        error_correction=_ERROR_LEVELS[error],
        box_size=box_size,
        border=border,
    )
    qr.add_data(text)
    qr.make(fit=True)
    return qr


def qr_to_ascii(text: str, error: str = "M", border: int = 1, invert: bool = True) -> str:
    """تولید نمایش ASCII از QR برای چاپ در ترمینال.

    با ``invert=True`` (پیش‌فرض)، ماژول‌های تیره به‌عنوان پس‌زمینه نمایش داده می‌شوند
    که برای ترمینال‌های تیره مناسب است.
    """
    qr = _make_qr(text, error=error, box_size=1, border=border)
    matrix = qr.get_matrix()
    rows = len(matrix)
    cols = len(matrix[0]) if rows else 0

    def render(top: bool, bottom: bool) -> str:
        if invert:
            top, bottom = not top, not bottom
        if top and bottom:
            return "█"
        if top:
            return "▀"
        if bottom:
            return "▄"
        return " "

    lines: list[str] = []
    for y in range(0, rows, 2):
        chars = []
        for x in range(cols):
            top = matrix[y][x]
            bottom = matrix[y + 1][x] if y + 1 < rows else False
            chars.append(render(top, bottom))
        lines.append("".join(chars))
    return "\n".join(lines)


def qr_to_image(
    text: str,
    output: Path,
    error: str = "M",
    box_size: int = 10,
    border: int = 4,
    fill_color: str = "black",
    back_color: str = "white",
) -> None:
    """ذخیرهٔ QR به‌صورت فایل تصویری."""
    qr = _make_qr(text, error=error, box_size=box_size, border=border)
    img = qr.make_image(fill_color=fill_color, back_color=back_color)
    img.save(str(output))