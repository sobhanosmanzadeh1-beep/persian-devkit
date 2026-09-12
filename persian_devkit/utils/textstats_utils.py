"""توابع کمکی آمار و تحلیل متن."""
from __future__ import annotations

import re
from collections import Counter

from persian_devkit.utils.text_utils import normalize

# الگوهای استخراج
EMAIL_RE = re.compile(r"[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}")
URL_RE = re.compile(r"https?://[^\s<>\"']+|www\.[^\s<>\"']+")
NUMBER_RE = re.compile(r"\b\d+(?:[.,]\d+)?\b")
HASHTAG_RE = re.compile(r"#[\w\u0600-\u06FF_]+")
MENTION_RE = re.compile(r"@[\w\u0600-\u06FF_]+")
IPV4_RE = re.compile(
    r"\b(?:(?:25[0-5]|2[0-4]\d|[01]?\d?\d)\.){3}"
    r"(?:25[0-5]|2[0-4]\d|[01]?\d?\d)\b"
)

# کلمات رایج فارسی (stopwords) — نمونهٔ کاربردی
PERSIAN_STOPWORDS: set[str] = {
    "و", "در", "به", "از", "که", "این", "را", "با", "است", "برای",
    "آن", "یک", "خود", "تا", "هم", "شد", "می", "او", "های", "بر",
    "اما", "یا", "اگر", "چون", "پس", "نیز", "بی", "هر", "چند",
    "چه", "کجا", "کی", "چگونه", "نه", "بله", "آری", "هست", "نیست",
    "بود", "باشد", "شود", "کرد", "کند", "دارد", "داشت", "باید",
    "شاید", "حتماً", "فقط", "دیگر", "همه", "هیچ", "بعضی", "کلی",
    "روی", "زیر", "بالا", "پایین", "داخل", "خارج", "پیش", "بعد",
    "قبل", "امروز", "دیروز", "فردا", "الان", "حالا", "سپس",
    "من", "تو", "ما", "شما", "ایشان", "اینجا", "آنجا", "کدام",
}

# الگوی نرمال‌سازی برای کلمات: حذف نیم‌فاصله و کاراکترهای خاص
_WORD_CLEAN_RE = re.compile(r"[^\w\u0600-\u06FF]+", re.UNICODE)


def text_info(text: str) -> dict:
    """آمار کامل متن: خط، کلمه، کاراکتر، جمله، پاراگراف."""
    lines = text.splitlines()
    paragraphs = [p for p in re.split(r"\n\s*\n", text) if p.strip()]
    words = text.split()
    chars = len(text)
    chars_no_space = sum(1 for c in text if not c.isspace())
    sentences = len(re.findall(r"[.!?؟]+", text))
    if sentences == 0 and text.strip():
        sentences = 1

    return {
        "lines": len(lines),
        "words": len(words),
        "chars": chars,
        "chars_no_space": chars_no_space,
        "sentences": sentences,
        "paragraphs": len(paragraphs),
        "avg_word_length": round(chars_no_space / len(words), 2) if words else 0.0,
        "avg_sentence_length": round(len(words) / sentences, 2) if sentences else 0.0,
    }


def word_frequency(text: str, top: int = 20, min_length: int = 1) -> list[tuple[str, int]]:
    """کلمات پرتکرار متن (نرمال‌شده)."""
    normalized = normalize(text)
    # پاک‌سازی و استخراج کلمات
    tokens = _WORD_CLEAN_RE.split(normalized)
    words = [
        w.lower() for w in tokens
        if w and len(w) >= min_length
    ]
    return Counter(words).most_common(top)


def word_frequency_no_stop(text: str, top: int = 20, min_length: int = 2) -> list[tuple[str, int]]:
    """کلمات پرتکرار بدون کلمات رایج فارسی."""
    normalized = normalize(text)
    tokens = _WORD_CLEAN_RE.split(normalized)
    words = [
        w.lower() for w in tokens
        if w and len(w) >= min_length and w.lower() not in PERSIAN_STOPWORDS
    ]
    return Counter(words).most_common(top)


def extract_emails(text: str) -> list[str]:
    """استخراج ایمیل‌ها."""
    return list(dict.fromkeys(EMAIL_RE.findall(text)))


def extract_urls(text: str) -> list[str]:
    """استخراج URLها."""
    return list(dict.fromkeys(URL_RE.findall(text)))


def extract_numbers(text: str) -> list[str]:
    """استخراج اعداد."""
    return list(dict.fromkeys(NUMBER_RE.findall(text)))


def extract_hashtags(text: str) -> list[str]:
    """استخراج هشتگ‌ها."""
    return list(dict.fromkeys(HASHTAG_RE.findall(text)))


def extract_mentions(text: str) -> list[str]:
    """استخراج منشن‌ها."""
    return list(dict.fromkeys(MENTION_RE.findall(text)))


def extract_ips(text: str) -> list[str]:
    """استخراج IPv4."""
    return list(dict.fromkeys(IPV4_RE.findall(text)))


def remove_stopwords(text: str) -> str:
    """حذف کلمات رایج فارسی از متن."""
    tokens = text.split()
    result = [w for w in tokens if _WORD_CLEAN_RE.sub("", w).lower() not in PERSIAN_STOPWORDS]
    return " ".join(result)


def unique_words(text: str) -> list[str]:
    """کلمات یکتا (با حفظ ترتیب ظهور)."""
    normalized = normalize(text)
    tokens = _WORD_CLEAN_RE.split(normalized)
    seen: list[str] = []
    seen_set: set[str] = set()
    for w in tokens:
        if w:
            low = w.lower()
            if low not in seen_set:
                seen_set.add(low)
                seen.append(w)
    return seen
