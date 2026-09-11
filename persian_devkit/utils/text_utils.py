"""توابع کمکی پاک‌سازی و پردازش متن فارسی."""
from __future__ import annotations

import re

# ی و ک عربی به فارسی
_ARABIC_TO_PERSIAN = str.maketrans(
    {
        "\u064a": "\u06cc",  # ي → ی
        "\u0643": "\u06a9",  # ك → ک
        "\u0649": "\u06cc",  # ى → ی
        "\u0629": "\u0647",  # ة → ه
        "\u06c0": "\u0647",  # ۀ → ه
    }
)

_DIACRITICS_RE = re.compile(r"[\u064b-\u065f\u0670]")
_MULTI_SPACE_RE = re.compile(r"[ \t]+")
_MULTI_NEWLINE_RE = re.compile(r"\n{3,}")
_SENTENCE_END_RE = re.compile(r"[.!?؟]+")

_ZWNJ = "\u200c"
_PREFIXES = ("نمی", "می")  # ترتیب مهم است (بلندتر اول)
_SUFFIXES = ("هایی", "های", "ترین", "ها", "تر")


def fix_halfspace(text: str) -> str:
    """اصلاح نیم‌فاصله در متن فارسی (می‌روم، کتاب‌ها، بهتر‌ترین)."""
    result = text
    # پیشوندها: می روم → می‌روم
    for prefix in _PREFIXES:
        result = re.sub(rf"(?<!\S){re.escape(prefix)}\s+", rf"{prefix}{_ZWNJ}", result)
    # پسوندها: کتاب ها → کتاب‌ها
    suffix_pattern = "|".join(re.escape(s) for s in _SUFFIXES)
    result = re.sub(rf"\s+({suffix_pattern})(?!\S)", rf"{_ZWNJ}\1", result)
    return result


def normalize(text: str) -> str:
    """یکسان‌سازی حروف عربی به فارسی، حذف اعراب و فاصله‌های اضافی."""
    result = text.translate(_ARABIC_TO_PERSIAN)
    result = _DIACRITICS_RE.sub("", result)
    result = _MULTI_SPACE_RE.sub(" ", result)
    result = _MULTI_NEWLINE_RE.sub("\n\n", result)
    return result.strip()


def reverse_text(text: str) -> str:
    """معکوس‌سازی کاراکترهای متن."""
    return text[::-1]


def text_stats(text: str) -> dict[str, int]:
    """محاسبهٔ آمار متن: کاراکتر، کلمه، خط، جمله."""
    lines = text.splitlines() or [""]
    words = text.split()
    chars = len(text)
    chars_no_space = sum(1 for c in text if not c.isspace())
    sentences = len(_SENTENCE_END_RE.findall(text))
    if sentences == 0 and text.strip():
        sentences = 1
    return {
        "chars": chars,
        "chars_no_space": chars_no_space,
        "words": len(words),
        "lines": len(lines),
        "sentences": sentences,
    }

#slug & case

_SLUG_KEEP = re.compile(r"[^\w\s\-]", re.UNICODE)
_SLUG_SPACES = re.compile(r"[\s\-_]+")


def to_slug(text: str, separator: str = "-", max_length: int = 0) -> str:
    """تبدیل متن (فارسی یا انگلیسی) به slug قابل استفاده در URL.

    نیم‌فاصله، اعراب و کاراکترهای غیرمجاز حذف یا جایگزین می‌شوند.
    """
    # اول نرمال‌سازی ی/ک عربی
    result = text.translate(_ARABIC_TO_PERSIAN)
    # حذف اعراب
    result = _DIACRITICS_RE.sub("", result)
    # نیم‌فاصله به فاصله (چون بعداً با separator یکی می‌شود)
    result = result.replace(_ZWNJ, " ")
    # حذف کاراکترهای غیرمجاز (نگه‌داشتن حروف، اعداد، خط تیره، آندرلاین)
    result = _SLUG_KEEP.sub("", result)
    # فاصله‌ها و جداکننده‌های تکراری
    result = _SLUG_SPACES.sub(separator, result).strip(separator)
    result = result.lower()
    if max_length > 0 and len(result) > max_length:
        result = result[:max_length].rstrip(separator)
    return result


_CASE_MODES = ("upper", "lower", "title", "capitalize", "swap")


def change_case(text: str, mode: str) -> str:
    """تغییر حالت حروف متن.

    حالت‌های پشتیبانی‌شده: upper, lower, title, capitalize, swap
    """
    if mode == "upper":
        return text.upper()
    if mode == "lower":
        return text.lower()
    if mode == "title":
        return text.title()
    if mode == "capitalize":
        return text.capitalize()
    if mode == "swap":
        return text.swapcase()
    raise ValueError(f"حالت ناشناخته: {mode}. مجاز: {', '.join(_CASE_MODES)}")


#diff


def diff_lines(a: str, b: str) -> list[tuple[str, str]]:
    """مقایسهٔ خطی دو متن.

    خروجی: لیستی از (علامت, خط) که علامت یکی از ' ', '-', '+' است.
    """
    import difflib

    a_lines = a.splitlines(keepends=False)
    b_lines = b.splitlines(keepends=False)
    result: list[tuple[str, str]] = []
    for line in difflib.unified_diff(a_lines, b_lines, lineterm="", n=0):
        if line.startswith("---") or line.startswith("+++"):
            continue
        if line.startswith("@@"):
            result.append((" ", line))
        elif line.startswith("-"):
            result.append(("-", line[1:]))
        elif line.startswith("+"):
            result.append(("+", line[1:]))
        else:
            result.append((" ", line[1:] if line.startswith(" ") else line))
    return result


#regex


def regex_test(pattern: str, text: str) -> dict:
    """اجرای regex روی متن و برگرداندن نتایج.

    خروجی: دیکشنری شامل match, groups و تعداد.
    """
    import re as _re

    try:
        compiled = _re.compile(pattern)
    except _re.error as exc:
        raise ValueError(f"الگوی regex نامعتبر: {exc}") from exc

    matches = compiled.findall(text)
    return {
        "pattern": pattern,
        "count": len(matches),
        "matches": [str(m) for m in matches],
        "is_match": bool(compiled.search(text)),
    }