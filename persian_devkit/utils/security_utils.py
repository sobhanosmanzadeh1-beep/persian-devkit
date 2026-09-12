"""توابع کمکی امنیت: JWT، رمزنگاری XOR، هش رمز، فینگرپرینت گواهی."""
from __future__ import annotations

import base64
import hashlib
import hmac
import json
import re
import secrets
import time
from typing import Optional


#JWT


def _b64url(data: bytes) -> str:
    """Base64 URL-safe بدون padding."""
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode("ascii")


def _b64url_decode(s: str) -> bytes:
    """Decode Base64 URL-safe با padding خودکار."""
    padding = "=" * (-len(s) % 4)
    return base64.urlsafe_b64decode(s + padding)


_JWT_ALGOS = {
    "HS256": hashlib.sha256,
    "HS384": hashlib.sha384,
    "HS512": hashlib.sha512,
}


def jwt_encode(payload: dict, secret: str, algorithm: str = "HS256") -> str:
    """ساخت JWT امضاشده با HMAC (HS256/HS384/HS512)."""
    if algorithm not in _JWT_ALGOS:
        raise ValueError(f"الگوریتم پشتیبانی‌نشده: {algorithm}")

    header = {"alg": algorithm, "typ": "JWT"}
    header_b64 = _b64url(json.dumps(header, separators=(",", ":")).encode())
    payload_b64 = _b64url(
        json.dumps(payload, separators=(",", ":"), default=str).encode()
    )

    signing_input = f"{header_b64}.{payload_b64}".encode()
    signature = hmac.new(
        secret.encode(), signing_input, _JWT_ALGOS[algorithm]
    ).digest()
    return f"{header_b64}.{payload_b64}.{_b64url(signature)}"


def jwt_decode(token: str, secret: str, verify: bool = True) -> dict:
    """رمزگشایی JWT و (اختیاری) بررسی امضا و انقضا."""
    parts = token.split(".")
    if len(parts) != 3:
        raise ValueError("JWT نامعتبر: باید ۳ بخش با نقطه جدا شده باشد")

    header_b64, payload_b64, sig_b64 = parts

    try:
        header = json.loads(_b64url_decode(header_b64))
        payload = json.loads(_b64url_decode(payload_b64))
    except (ValueError, json.JSONDecodeError) as exc:
        raise ValueError(f"JWT نامعتبر: {exc}") from exc

    if verify:
        alg = header.get("alg", "HS256")
        if alg not in _JWT_ALGOS:
            raise ValueError(f"الگوریتم پشتیبانی‌نشده: {alg}")

        signing_input = f"{header_b64}.{payload_b64}".encode()
        expected_sig = hmac.new(
            secret.encode(), signing_input, _JWT_ALGOS[alg]
        ).digest()
        actual_sig = _b64url_decode(sig_b64)

        if not hmac.compare_digest(expected_sig, actual_sig):
            raise ValueError("امضای JWT نامعتبر است")

        if "exp" in payload and time.time() > payload["exp"]:
            raise ValueError("JWT منقضی شده است")

    return payload


#رمزنگاری XOR


def xor_encrypt(text: str, key: str) -> str:
    """رمزگذاری XOR ساده (خروجی Base64). برای پنهان‌سازی سریع، نه امنیت واقعی."""
    if not key:
        raise ValueError("کلید نمی‌تواند خالی باشد")
    data = text.encode("utf-8")
    key_bytes = key.encode("utf-8")
    encrypted = bytes(b ^ key_bytes[i % len(key_bytes)] for i, b in enumerate(data))
    return base64.b64encode(encrypted).decode("ascii")


def xor_decrypt(encoded: str, key: str) -> str:
    """رمزگشایی XOR."""
    if not key:
        raise ValueError("کلید نمی‌تواند خالی باشد")
    try:
        data = base64.b64decode(encoded)
    except Exception as exc:
        raise ValueError(f"Base64 نامعتبر: {exc}") from exc

    key_bytes = key.encode("utf-8")
    decrypted = bytes(b ^ key_bytes[i % len(key_bytes)] for i, b in enumerate(data))
    try:
        return decrypted.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise ValueError("کلید اشتباه یا دادهٔ خراب") from exc


#password


def hash_password(password: str, salt: Optional[str] = None) -> str:
    """هش رمز عبور با PBKDF2-SHA256. فرمت: pbkdf2_sha256$iter$salt$hash."""
    iterations = 260_000
    if salt is None:
        salt = secrets.token_hex(16)
    dk = hashlib.pbkdf2_hmac(
        "sha256", password.encode("utf-8"), salt.encode("utf-8"), iterations
    )
    return f"pbkdf2_sha256${iterations}${salt}${dk.hex()}"


def verify_password(password: str, hashed: str) -> bool:
    """بررسی رمز عبور در برابر هش PBKDF2."""
    try:
        algo, iter_s, salt, expected = hashed.split("$", 3)
    except ValueError:
        return False
    if algo != "pbkdf2_sha256":
        return False
    try:
        iterations = int(iter_s)
    except ValueError:
        return False
    dk = hashlib.pbkdf2_hmac(
        "sha256", password.encode("utf-8"), salt.encode("utf-8"), iterations
    )
    return hmac.compare_digest(dk.hex(), expected)


#secret


def generate_secret(length: int = 32) -> str:
    """تولید کلید امن (URL-safe) مناسب JWT یا متغیر محیطی."""
    if length < 16:
        raise ValueError("طول کلید باید حداقل ۱۶ کاراکتر باشد")
    return secrets.token_urlsafe(length)[:length]


#cert


def cert_info(cert_pem: str) -> dict:
    """اطلاعات پایهٔ گواهی PEM: فینگرپرینت SHA-256/SHA-1 و طول DER."""
    if "-----BEGIN CERTIFICATE-----" not in cert_pem:
        raise ValueError("PEM نامعتبر: بلوک CERTIFICATE یافت نشد")

    match = re.search(
        r"-----BEGIN CERTIFICATE-----\s*(.+?)\s*-----END CERTIFICATE-----",
        cert_pem,
        re.DOTALL,
    )
    if not match:
        raise ValueError("PEM نامعتبر")

    b64 = re.sub(r"\s+", "", match.group(1))
    try:
        der = base64.b64decode(b64, validate=True)
    except Exception as exc:
        raise ValueError(f"Base64 نامعتبر در PEM: {exc}") from exc

    return {
        "pem_length": len(cert_pem),
        "der_length": len(der),
        "sha256_fingerprint": hashlib.sha256(der).hexdigest(),
        "sha1_fingerprint": hashlib.sha1(der).hexdigest(),
    }