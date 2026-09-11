"""توابع کمکی کریپتوگرافی، هش، رمز و base64."""
from __future__ import annotations

import base64
import hashlib
import math
import secrets
import string
from pathlib import Path

HASH_ALGOS = ("md5", "sha1", "sha256", "sha512", "blake2b", "blake2s")

# مجموعه‌های کاراکتری برای تولید رمز
PASSWORD_SETS: dict[str, str] = {
    "lower": string.ascii_lowercase,
    "upper": string.ascii_uppercase,
    "digits": string.digits,
    "symbols": "!@#$%^&*()-_=+[]{};:,.<>?/",
}

# الفبای Nano ID (URL-safe)
_NANOID_ALPHABET = string.ascii_letters + string.digits + "_-"


#hash


def hash_text(text: str, algo: str = "sha256") -> str:
    """هش یک رشتهٔ متنی را برمی‌گرداند."""
    if algo not in HASH_ALGOS:
        raise ValueError(f"الگوریتم پشتیبانی‌نشده: {algo}")
    h = hashlib.new(algo)
    h.update(text.encode("utf-8"))
    return h.hexdigest()


def hash_file(path: Path, algo: str = "sha256", chunk: int = 1 << 20) -> str:
    """هش یک فایل را به‌صورت chunk-by-chunk حساب می‌کند (مناسب فایل‌های بزرگ)."""
    if algo not in HASH_ALGOS:
        raise ValueError(f"الگوریتم پشتیبانی‌نشده: {algo}")
    h = hashlib.new(algo)
    with path.open("rb") as f:
        while True:
            block = f.read(chunk)
            if not block:
                break
            h.update(block)
    return h.hexdigest()


#base64


def b64_encode(text: str, url_safe: bool = False) -> str:
    """رمزگذاری Base64 با پشتیبانی UTF-8."""
    raw = text.encode("utf-8")
    if url_safe:
        return base64.urlsafe_b64encode(raw).decode("ascii")
    return base64.b64encode(raw).decode("ascii")


def b64_decode(text: str, url_safe: bool = False) -> str:
    """رمزگشایی Base64 به UTF-8."""
    cleaned = text.strip().encode("ascii")
    try:
        if url_safe:
            raw = base64.urlsafe_b64decode(cleaned)
        else:
            raw = base64.b64decode(cleaned, validate=True)
    except Exception as exc:
        raise ValueError(f"Base64 نامعتبر: {exc}") from exc
    return raw.decode("utf-8")


#password


def generate_password(
    length: int = 16,
    use_lower: bool = True,
    use_upper: bool = True,
    use_digits: bool = True,
    use_symbols: bool = True,
) -> str:
    """تولید رمز عبور امن با مجموعه‌های کاراکتری انتخابی."""
    pools: list[str] = []
    if use_lower:
        pools.append(PASSWORD_SETS["lower"])
    if use_upper:
        pools.append(PASSWORD_SETS["upper"])
    if use_digits:
        pools.append(PASSWORD_SETS["digits"])
    if use_symbols:
        pools.append(PASSWORD_SETS["symbols"])

    if not pools:
        raise ValueError("حداقل یک مجموعهٔ کاراکتری باید فعال باشد.")
    if length < len(pools):
        raise ValueError(
            f"طول رمز باید حداقل {len(pools)} باشد تا از هر مجموعه یک کاراکتر بیاید."
        )

    # تضمین حداقل یک کاراکتر از هر مجموعه
    chars = [secrets.choice(pool) for pool in pools]
    all_chars = "".join(pools)
    chars.extend(secrets.choice(all_chars) for _ in range(length - len(pools)))
    # Fisher-Yates shuffle امن
    for i in range(len(chars) - 1, 0, -1):
        j = secrets.randbelow(i + 1)
        chars[i], chars[j] = chars[j], chars[i]
    return "".join(chars)


def password_strength(password: str) -> dict:
    """امتیاز قدرت رمز عبور (۰ تا ۱۰۰) و برچسب."""
    if not password:
        return {"score": 0, "label": "خالی", "entropy": 0.0}

    pools = 0
    if any(c.islower() for c in password):
        pools += 26
    if any(c.isupper() for c in password):
        pools += 26
    if any(c.isdigit() for c in password):
        pools += 10
    if any(c in PASSWORD_SETS["symbols"] for c in password):
        pools += len(PASSWORD_SETS["symbols"])

    if pools == 0:
        entropy = 0.0
    else:
        entropy = len(password) * math.log2(pools)

    # نگاشت آنتروپی به امتیاز ۰-۱۰۰
    # < 28 → خیلی ضعیف، 28-35 ضعیف، 36-59 متوسط، 60-127 قوی، 128+ خیلی قوی
    if entropy < 28:
        score, label = 15, "خیلی ضعیف"
    elif entropy < 36:
        score, label = 30, "ضعیف"
    elif entropy < 60:
        score, label = 55, "متوسط"
    elif entropy < 128:
        score, label = 80, "قوی"
    else:
        score, label = 100, "خیلی قوی"

    return {"score": score, "label": label, "entropy": round(entropy, 1)}


#nanoid


def nanoid(length: int = 21) -> str:
    """تولید شناسهٔ کوتاه Nano ID با الفبای URL-safe."""
    if length < 1:
        raise ValueError("طول باید حداقل ۱ باشد.")
    return "".join(secrets.choice(_NANOID_ALPHABET) for _ in range(length))