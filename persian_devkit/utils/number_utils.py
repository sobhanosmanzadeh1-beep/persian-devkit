"""تبدیل و قالب‌بندی اعداد با پشتیبانی فارسی."""
from __future__ import annotations

PERSIAN_DIGITS = "۰۱۲۳۴۵۶۷۸۹"
ENGLISH_DIGITS = "0123456789"
ARABIC_DIGITS = "٠١٢٣٤٥٦٧٨٩"

_ONES = ["", "یک", "دو", "سه", "چهار", "پنج", "شش", "هفت", "هشت", "نه"]
_TEENS = [
    "ده", "یازده", "دوازده", "سیزده", "چهارده",
    "پانزده", "شانزده", "هفده", "هجده", "نوزده",
]
_TENS = ["", "", "بیست", "سی", "چهل", "پنجاه", "شصت", "هفتاد", "هشتاد", "نود"]
_HUNDREDS = ["", "صد", "دویست", "سیصد", "چهارصد", "پانصد", "ششصد", "هفتصد", "هشتصد", "نهصد"]
_SCALES = ["", " هزار", " میلیون", " میلیارد", " بیلیون"]


def to_persian_digits(value: str) -> str:
    """تبدیل ارقام لاتین/عربی به ارقام فارسی."""
    table = str.maketrans(
        ENGLISH_DIGITS + ARABIC_DIGITS,
        PERSIAN_DIGITS + PERSIAN_DIGITS,
    )
    return value.translate(table)


def to_english_digits(value: str) -> str:
    """تبدیل ارقام فارسی/عربی به ارقام لاتین."""
    table = str.maketrans(
        PERSIAN_DIGITS + ARABIC_DIGITS,
        ENGLISH_DIGITS + ENGLISH_DIGITS,
    )
    return value.translate(table)


def format_thousands(n: int) -> str:
    """قالب‌بندی عدد با جداکنندهٔ هزارگان."""
    return f"{n:,}"


def _three_digit_to_words(n: int) -> str:
    """تبدیل عدد سه‌رقمی (۰ تا ۹۹۹) به حروف فارسی."""
    parts: list[str] = []
    h, rem = divmod(n, 100)
    if h:
        parts.append(_HUNDREDS[h])
    if 10 <= rem < 20:
        parts.append(_TEENS[rem - 10])
    else:
        t, o = divmod(rem, 10)
        if t:
            parts.append(_TENS[t])
        if o:
            parts.append(_ONES[o])
    return " و ".join(parts)


def number_to_words(n: int) -> str:
    """تبدیل عدد صحیح به معادل نوشتاری فارسی."""
    if n == 0:
        return "صفر"
    if n < 0:
        return "منفی " + number_to_words(-n)

    groups: list[int] = []
    value = n
    while value > 0:
        groups.append(value % 1000)
        value //= 1000

    parts: list[str] = []
    for idx in range(len(groups) - 1, -1, -1):
        group = groups[idx]
        if group == 0:
            continue
        text = _three_digit_to_words(group)
        parts.append(text + _SCALES[idx])
    return " و ".join(parts)