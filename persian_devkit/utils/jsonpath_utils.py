"""پیاده‌سازی سادهٔ JSONPath با پشتیبانی از dot و [index] و [*]."""
from __future__ import annotations

import re
from typing import Any


class JSONPathError(ValueError):
    """خطا در مسیر JSONPath."""


# توکن‌ها: .key یا [0] یا ["key"] یا [*] یا key در ابتدای مسیر
_TOKEN_RE = re.compile(
    r"""
      \.([A-Za-z_][\w\-]*)          # .key
    | \[\s*(\d+)\s*\]               # [0]
    | \[\s*['"]([^'"]+)['"]\s*\]    # ["key"]
    | \[\s*(\*)\s*\]                # [*]
    | ^([A-Za-z_][\w\-]*)           # key در ابتدای مسیر (بدون نقطه)
    """,
    re.VERBOSE,
)


def _tokenize(path: str) -> list[tuple[str, Any]]:
    """مسیر را به توکن‌های (نوع, مقدار) تجزیه می‌کند."""
    p = path.strip()
    if p == "" or p == "$":
        return []

    if p.startswith("$"):
        p = p[1:]

    tokens: list[tuple[str, Any]] = []
    pos = 0
    while pos < len(p):
        m = _TOKEN_RE.match(p, pos)
        if not m:
            raise JSONPathError(f"مسیر نامعتبر در موقعیت {pos}: {p[pos:pos+20]!r}")
        key1, idx, key2, wildcard, key3 = m.groups()
        if key1 is not None:
            tokens.append(("key", key1))
        elif idx is not None:
            tokens.append(("index", int(idx)))
        elif key2 is not None:
            tokens.append(("key", key2))
        elif wildcard is not None:
            tokens.append(("wildcard", None))
        elif key3 is not None:
            tokens.append(("key", key3))
        pos = m.end()
    return tokens


def query(data: Any, path: str) -> Any:
    """اجرای مسیر روی داده و برگرداندن مقدار.

    مسیرهای پشتیبانی‌شده:
      .user.name           → کلید تودرتو
      .items[0]            → اندیس آرایه
      .items[*].name       → همهٔ عناصر
      ["key with space"]   → کلید با کاراکتر خاص
      $                    → خود داده
    """
    tokens = _tokenize(path)
    results: list[Any] = [data]

    for kind, value in tokens:
        next_results: list[Any] = []
        for item in results:
            if kind == "key":
                if isinstance(item, dict) and value in item:
                    next_results.append(item[value])
            elif kind == "index":
                if isinstance(item, list) and -len(item) <= value < len(item):
                    next_results.append(item[value])
            elif kind == "wildcard":
                if isinstance(item, list):
                    next_results.extend(item)
                elif isinstance(item, dict):
                    next_results.extend(item.values())
        results = next_results

    if len(results) == 1:
        return results[0]
    return results


def query_many(data: Any, path: str) -> list[Any]:
    """مثل query اما همیشه لیست برمی‌گرداند."""
    result = query(data, path)
    if isinstance(result, list):
        return result
    return [result]