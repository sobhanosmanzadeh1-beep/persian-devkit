"""اعداد ترتیبی و نوشتاری فارسی."""
from __future__ import annotations

from persian_devkit.utils.number_utils import _three_digit_to_words  # type: ignore

_ORDINALS_FA = {
    1: "اول", 2: "دوم", 3: "سوم", 4: "چهارم", 5: "پنجم",
    6: "ششم", 7: "هفتم", 8: "هشتم", 9: "نهم", 10: "دهم",
    11: "یازدهم", 12: "دوازدهم", 13: "سیزدهم", 14: "چهاردهم",
    15: "پانزدهم", 16: "شانزدهم", 17: "هفدهم", 18: "هجدهم",
    19: "نوزدهم", 20: "بیستم",
}


def to_ordinal(n: int) -> str:
    """عدد را به شکل ترتیبی فارسی برمی‌گرداند.

    ۱ → اول
    ۲ → دوم
    ۳ → سوم
    ۲۱ → بیست و یکم
    ۳۰ → سی‌ام
    ۱۰۰ → صدم
    ۱۰۰۰ → هزارم
    """
    if n <= 0:
        raise ValueError(f"عدد باید مثبت باشد، دریافت شد: {n}")

    if n == 1:
        return "اول"

    if n in _ORDINALS_FA:
        return _ORDINALS_FA[n]

    # ۲۱ تا ۹۹
    if n < 100:
        tens, ones = divmod(n, 10)
        tens_word = _two_digit_words(tens * 10)
        if ones == 0:
            # 20, 30, 40, ... → بیستم، سی‌ام، چهلم
            return _make_ordinal_simple(n)
        if ones == 1:
            # 21, 31, 41, ... → بیست و یکم
            return f"{tens_word} و یکم"
        return f"{tens_word} و {_ORDINALS_FA[ones]}"

    # ۱۰۰ به بالا
    return _make_ordinal_simple(n)

def _two_digit_words(n: int) -> str:
    """کلمات دو رقمی (مثلاً 20 → بیست)."""
    words = {
        20: "بیست", 30: "سی", 40: "چهل", 50: "پنجاه",
        60: "شصت", 70: "هفتاد", 80: "هشتاد", 90: "نود",
    }
    return words.get(n, str(n))


def _make_ordinal_simple(n: int) -> str:
    """ساخت ترتیبی برای اعداد بزرگ.

    قاعده:
      - اگر آخرین کلمه به «ی» ختم شود → «‌ام» (نیم‌فاصله + ام): سی → سی‌ام
      - اگر آخرین کلمه به «ه» ختم شود → «ام»: پنجاه → پنجاهم
      - در غیر این صورت → «م»: بیست → بیستم، صد → صدم
    """
    words = _three_digit_to_words(n)
    if not words:
        return str(n)
    last = words.split()[-1]
    if last.endswith("ی"):
        return words + "\u200cام"  # نیم‌فاصله + ام
    if last.endswith("ه"):
        return words + "ام"
    return words + "م"