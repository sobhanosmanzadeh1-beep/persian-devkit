"""توابع کمکی DNS lookup."""
from __future__ import annotations

import socket
from typing import Optional

try:
    import dns.resolver  # type: ignore
    _HAS_DNSPYTHON = True
except ImportError:
    _HAS_DNSPYTHON = False


RECORD_TYPES = ("A", "AAAA", "MX", "NS", "TXT", "CNAME", "SOA")


def lookup_a(domain: str) -> list[str]:
    """رکورد A (IPv4)."""
    try:
        return list({addr[4][0] for addr in socket.getaddrinfo(domain, None, socket.AF_INET)})
    except socket.gaierror:
        return []


def lookup_aaaa(domain: str) -> list[str]:
    """رکورد AAAA (IPv6)."""
    try:
        return list({addr[4][0] for addr in socket.getaddrinfo(domain, None, socket.AF_INET6)})
    except socket.gaierror:
        return []


def lookup(domain: str, record_type: str = "A") -> list[str]:
    """جستجوی رکورد DNS. اگر dnspython نصب باشد از آن استفاده می‌کند."""
    rtype = record_type.upper()

    if rtype == "A":
        return lookup_a(domain)
    if rtype == "AAAA":
        return lookup_aaaa(domain)

    # بقیهٔ رکوردها نیاز به dnspython دارند
    if not _HAS_DNSPYTHON:
        raise ValueError(
            f"برای رکورد {rtype} باید dnspython نصب باشد: pip install dnspython"
        )

    try:
        answers = dns.resolver.resolve(domain, rtype, lifetime=5.0)
        results: list[str] = []
        for rdata in answers:
            if rtype == "MX":
                results.append(f"{rdata.preference} {rdata.exchange}")
            else:
                results.append(str(rdata))
        return results
    except Exception as exc:
        raise ValueError(f"خطا در جستجوی {rtype} برای {domain}: {exc}") from exc


def reverse_lookup(ip: str) -> Optional[str]:
    """جستجوی معکوس IP."""
    try:
        return socket.gethostbyaddr(ip)[0]
    except (socket.herror, socket.gaierror, OSError):
        return None