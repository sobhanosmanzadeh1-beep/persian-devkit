"""مرتب‌سازی با الفبای فارسی."""
from __future__ import annotations

from persian_devkit.utils.text_utils import normalize

# ترتیب الفبای فارسی
_PERSIAN_ALPHABET = (
    "آابپتثجچحخدذرزژسشصضطظعغفقکگلمنوهی"
    "۰۱۲۳۴۵۶۷۸۹"
    " "
)

_ALPHABET_INDEX: dict[str, int] = {
    ch: i for i, ch in enumerate(_PERSIAN_ALPHABET)
}


def _sort_key(text: str) -> tuple:
    """کلید مرتب‌سازی برای متن فارسی."""
    normalized = normalize(text)
    key: list[int] = []
    for ch in normalized:
        key.append(_ALPHABET_INDEX.get(ch, 1000))  # ناشناخته‌ها به آخر
    return tuple(key)


def sort_lines(lines: list[str], reverse: bool = False) -> list[str]:
    """مرتب‌سازی خطوط بر اساس الفبای فارسی.

    خطوط خالی به ابتدا می‌روند (در حالت عادی).
    """
    non_empty = [ln for ln in lines if ln.strip()]
    empty = [ln for ln in lines if not ln.strip()]
    non_empty.sort(key=_sort_key, reverse=reverse)
    if reverse:
        return non_empty + empty
    return empty + non_empty


def unique_lines(lines: list[str], case_sensitive: bool = False) -> list[str]:
    """حذف خطوط تکراری با حفظ ترتیب."""
    seen: set[str] = set()
    result: list[str] = []
    for ln in lines:
        key = ln if case_sensitive else normalize(ln).lower()
        if key not in seen:
            seen.add(key)
            result.append(ln)
    return result