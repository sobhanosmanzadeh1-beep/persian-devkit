"""توابع کمکی کار با URL."""
from __future__ import annotations

from urllib.parse import (
    parse_qs,
    parse_qsl,
    quote,
    unquote,
    urlencode,
    urlparse,
    urlunparse,
)


def url_encode(text: str, safe: str = "") -> str:
    """درصد-رمزگذاری متن برای استفاده در URL."""
    return quote(text, safe=safe)


def url_decode(text: str) -> str:
    """رمزگشایی متن درصد-رمزگذاری‌شده."""
    return unquote(text)


def parse_url(url: str) -> dict:
    """تجزیهٔ URL به اجزای سازنده."""
    parsed = urlparse(url)
    query = dict(parse_qsl(parsed.query, keep_blank_values=True))
    return {
        "scheme": parsed.scheme,
        "netloc": parsed.netloc,
        "host": parsed.hostname or "",
        "port": parsed.port,
        "path": parsed.path,
        "query": query,
        "fragment": parsed.fragment,
        "username": parsed.username,
        "password": parsed.password,
    }


def build_query(params: dict[str, str]) -> str:
    """ساخت query string از دیکشنری."""
    return urlencode(params)


def encode_query(params: dict[str, str]) -> str:
    """مترادف build_query برای خوانایی."""
    return build_query(params)


def decode_query(text: str) -> dict[str, list[str]]:
    """تجزیهٔ query string به دیکشنری (مقادیر چندگانه → لیست)."""
    return parse_qs(text, keep_blank_values=True)