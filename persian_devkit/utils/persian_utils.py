"""توابع پیشرفتهٔ پردازش متن فارسی (همزه، کشیده، پیشوند/پسوند)."""
from __future__ import annotations

import unicodedata


#همزه
_HAMZA_MAP = {
    "أ": "ا",
    "إ": "ا",
    "آ": "ا",   # ← اینجا "ا" (نه "آ")
    "ؤ": "و",
    "ئ": "ی",
    "ٱ": "ا",
}

_HAMZA_CHARS = set(_HAMZA_MAP.keys())


def normalize_hamza(text: str, keep_aa: bool = True) -> str:
    """یکسان‌سازی انواع همزه.

    - أ، إ، ٱ → ا
    - ؤ → و
    - ئ → ی
    - آ → آ (اگر keep_aa باشد) یا ا
    """
    result: list[str] = []
    for ch in text:
        if ch == "آ":
            result.append("آ" if keep_aa else "ا")
        elif ch in _HAMZA_MAP:
            result.append(_HAMZA_MAP[ch])
        else:
            result.append(ch)
    return "".join(result)


def has_hamza(text: str) -> bool:
    """آیا متن حاوی همزهٔ غیراستاندارد است؟"""
    return any(ch in _HAMZA_CHARS for ch in text)


#کشیده

_KASHIDA = "\u0640"  # ARABIC TATWEEL


def add_kashida(word: str, target_length: int) -> str:
    """افزودن کشیده به یک کلمه تا رسیدن به طول هدف (تقریبی).

    کشیده به حروفی که بعدشان حرف متصل می‌آید اضافه می‌شود.
    """
    if target_length <= len(word):
        return word

    needed = target_length - len(word)
    # حروفی که به حرف بعدی می‌چسبند (اتصال از چپ)
    joinable = set("بپتثجچحخسشصضطظعغفقکگلمنهی")

    result: list[str] = []
    for i, ch in enumerate(word):
        result.append(ch)
        # اگر این حرف متصل است و حرف بعدی هم وجود دارد، کشیده اضافه کن
        if needed > 0 and ch in joinable and i < len(word) - 1:
            next_ch = word[i + 1]
            if next_ch not in "اآدذرزژو":
                result.append(_KASHIDA)
                needed -= 1
    return "".join(result)


def remove_kashida(text: str) -> str:
    """حذف همهٔ کشیده‌ها از متن."""
    return text.replace(_KASHIDA, "")


def justify_line(text: str, width: int) -> str:
    """ترازبندی یک خط فارسی با کشیده.

    کلمات را با فاصله یکنواخت تقسیم می‌کند و کشیده‌ها را به بلندترین کلمات اضافه می‌کند.
    """
    words = text.split()
    if len(words) < 2:
        return add_kashida(text, width) if len(text) < width else text

    current_len = len(text)
    if current_len >= width:
        return text

    # فاصله‌های اضافی به بلندترین کلمات داده می‌شود
    extra = width - current_len
    sorted_idx = sorted(range(len(words)), key=lambda i: -len(words[i]))

    # توزیع نوبتی
    i = 0
    while extra > 0 and i < len(sorted_idx):
        idx = sorted_idx[i]
        # به هر کلمه یک کشیده اضافه کن
        words[idx] = add_kashida(words[idx], len(words[idx]) + 1)
        extra -= 1
        i += 1
        if i == len(sorted_idx):
            i = 0  # از اول شروع کن اگر باز جا داریم

    return " ".join(words)


#پیشوند/پسوند


_PREFIXES = ("نمی", "می", "بی")  # ترتیب مهم: بلندتر اول


# کلمات استثنا: با پیشوند شروع می‌شوند اما پیشوند نیستند
_PREFIX_EXCEPTIONS = {
    "میلیون", "میلیارد", "میلی", "میان", "میانه", "میانگین", "میوه",
    "میز", "میکروب", "میکروسکوپ", "میلیمتر", "مینا", "میمون", "میکا",
    "بیمار", "بیمه", "بیرون", "بی‌سواد", "بیابان", "بیل", "بین",
    "بیست", "بی‌نهایت",
}


def fix_prefixes(text: str) -> str:
    """اصلاح پیشوندهای چسبیده با نیم‌فاصله.

    «میروم» → «می‌روم»، «نمیدانم» → «نمی‌دانم»
    کلماتی مثل «میلیون»، «بیمار» که با پیشوند شروع می‌شوند ولی پیشوند نیستند، حفظ می‌شوند.
    """
    import re

    zwnj = "\u200c"

    def _replace_word(match: re.Match) -> str:
        word = match.group(0)
        # اگر کلمه در لیست استثناست، برش گردان
        if word in _PREFIX_EXCEPTIONS:
            return word

        for prefix in _PREFIXES:
            if word.startswith(prefix) and len(word) > len(prefix) + 1:
                remainder = word[len(prefix):]
                # اگر بعد از پیشوند نیم‌فاصله یا فاصله است، رد کن
                if remainder.startswith(zwnj) or remainder.startswith(" "):
                    return word
                return prefix + zwnj + remainder
        return word

    # الگو: کل کلمه‌های فارسی
    return re.sub(r"[\u0600-\u06FF\u200c]+", _replace_word, text)


_SUFFIXES = ("هایی", "های", "ترین", "ها", "تر")  # ترتیب مهم


def fix_suffixes(text: str) -> str:
    """اصلاح پسوندهای چسبیده با نیم‌فاصله: «کتابها» → «کتاب‌ها»، «بهتری» → «بهتری»."""
    zwnj = "\u200c"
    result = text
    for suffix in _SUFFIXES:
        # الگو: حرف فارسی + suffix در انتهای کلمه
        import re

        pattern = rf"([\u0600-\u06FF])({suffix})(?![\w\u0600-\u06FF])"
        result = re.sub(pattern, rf"\1{zwnj}\2", result)
    return result


def fix_spacing(text: str) -> str:
    """ترکیب اصلاح پیشوند و پسوند."""
    return fix_suffixes(fix_prefixes(text))


#charinfo


def char_info(char: str) -> dict:
    """اطلاعات یونیکد یک کاراکتر."""
    if len(char) != 1:
        raise ValueError("فقط یک کاراکتر مجاز است")
    cp = ord(char)
    try:
        name = unicodedata.name(char)
    except ValueError:
        name = "<unnamed>"
    category = unicodedata.category(char)
    return {
        "char": char,
        "code_point": f"U+{cp:04X}",
        "decimal": cp,
        "hex": hex(cp),
        "name": name,
        "category": category,
        "is_letter": char.isalpha(),
        "is_digit": char.isdigit(),
        "is_persian": is_persian_char(char),
        "is_zwnj": char == "\u200c",
        "is_kashida": char == _KASHIDA,
    }


def is_persian_char(ch: str) -> bool:
    """آیا کاراکتر در محدودهٔ فارسی/عربی است؟"""
    cp = ord(ch)
    return (
        0x0600 <= cp <= 0x06FF  # Arabic
        or 0xFB50 <= cp <= 0xFDFF  # Arabic Presentation Forms-A
        or 0xFE70 <= cp <= 0xFEFF  # Arabic Presentation Forms-B
    )


def text_to_visual(text: str, base_dir: str = "R") -> str:
    """تبدیل متن منطقی به ترتیب بصری (برای نمایش صحیح در ترمینال‌های LTR).

    برای اکثر ترمینال‌های مدرن نیازی نیست، اما روی بعضی محیط‌ها مفید است.
    """
    try:
        from bidi.algorithm import get_display
    except ImportError:
        raise RuntimeError("python-bidi نصب نیست: pip install python-bidi")

    return get_display(text, base_dir=base_dir)


def text_to_logical(text: str) -> str:
    """برعکس text_to_visual — تبدیل متن بصری به منطقی."""
    # python-bidi این را مستقیم ارائه نمی‌دهد، پس فقط برمی‌گردانیم
    return text