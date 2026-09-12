"""توابع کمکی HTTP."""
from __future__ import annotations

import time
from typing import Optional

import httpx


def http_request(
    url: str,
    method: str = "GET",
    headers: Optional[dict[str, str]] = None,
    timeout: float = 10.0,
    follow_redirects: bool = True,
) -> dict:
    """ارسال درخواست HTTP و برگرداندن اطلاعات کامل."""
    method = method.upper()
    if method not in ("GET", "POST", "PUT", "DELETE", "HEAD", "PATCH", "OPTIONS"):
        raise ValueError(f"متد نامعتبر: {method}")

    start = time.perf_counter()
    try:
        with httpx.Client(
            timeout=timeout,
            follow_redirects=follow_redirects,
            headers=headers or {},
        ) as client:
            response = client.request(method, url)
        elapsed = (time.perf_counter() - start) * 1000  # ms
    except httpx.TimeoutException as exc:
        raise ValueError(f"timeout: {exc}") from exc
    except httpx.ConnectError as exc:
        raise ValueError(f"خطای اتصال: {exc}") from exc
    except httpx.HTTPError as exc:
        raise ValueError(f"خطای HTTP: {exc}") from exc

    return {
        "status": response.status_code,
        "reason": response.reason_phrase,
        "url": str(response.url),
        "method": method,
        "headers": dict(response.headers),
        "elapsed_ms": round(elapsed, 2),
        "content_length": len(response.content),
        "content_type": response.headers.get("content-type", ""),
        "redirected": str(response.url) != url,
        "history": [str(r.url) for r in response.history],
        "text_preview": response.text[:500] if "text" in response.headers.get("content-type", "") else "",
    }