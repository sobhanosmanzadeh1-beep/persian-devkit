"""تست‌های Batch 11 — امنیت."""
from __future__ import annotations

import time

import pytest
from typer.testing import CliRunner

from persian_devkit.main import app
from persian_devkit.utils.security_utils import (
    cert_info,
    generate_secret,
    hash_password,
    jwt_decode,
    jwt_encode,
    verify_password,
    xor_decrypt,
    xor_encrypt,
)

runner = CliRunner()


#JWT


def test_jwt_roundtrip():
    token = jwt_encode({"sub": "ali", "role": "admin"}, "test-secret")
    decoded = jwt_decode(token, "test-secret")
    assert decoded["sub"] == "ali"
    assert decoded["role"] == "admin"


def test_jwt_invalid_signature():
    token = jwt_encode({"a": 1}, "secret1")
    with pytest.raises(ValueError):
        jwt_decode(token, "secret2")


def test_jwt_invalid_format():
    with pytest.raises(ValueError):
        jwt_decode("invalid.token", "x")


def test_jwt_expired():
    token = jwt_encode({"exp": int(time.time()) - 60}, "s")
    with pytest.raises(ValueError, match="منقضی"):
        jwt_decode(token, "s")


def test_jwt_algorithms():
    for algo in ("HS256", "HS384", "HS512"):
        token = jwt_encode({"x": 1}, "s", algorithm=algo)
        assert jwt_decode(token, "s")["x"] == 1


def test_jwt_invalid_algorithm():
    with pytest.raises(ValueError):
        jwt_encode({"x": 1}, "s", algorithm="RS256")


def test_jwt_decode_without_verify():
    token = jwt_encode({"x": 1}, "any-secret")
    # بدون verify → هر secret قبول می‌شود
    assert jwt_decode(token, "wrong", verify=False)["x"] == 1


#XOR encrypt


def test_xor_roundtrip_ascii():
    assert xor_decrypt(xor_encrypt("hello", "key"), "key") == "hello"


def test_xor_roundtrip_persian():
    text = "سلام دنیا"
    assert xor_decrypt(xor_encrypt(text, "کلید"), "کلید") == text


def test_xor_wrong_key_gives_wrong_result():
    """با کلید اشتباه، نتیجه غلط ولی معتبر برمی‌گردد (نه خطا)."""
    encoded = xor_encrypt("hello world", "key1")
    result = xor_decrypt(encoded, "key2")
    assert result != "hello world"


def test_xor_empty_key():
    with pytest.raises(ValueError):
        xor_encrypt("x", "")


def test_xor_invalid_base64():
    with pytest.raises(ValueError):
        xor_decrypt("!!!not-base64!!!", "key")


#hash_password


def test_hash_password_verify():
    h = hash_password("mysecret123")
    assert verify_password("mysecret123", h)
    assert not verify_password("wrong", h)


def test_hash_password_salt_unique():
    h1 = hash_password("same")
    h2 = hash_password("same")
    assert h1 != h2


def test_hash_password_invalid_format():
    assert not verify_password("x", "invalid-hash")


#secret


def test_generate_secret_length():
    s = generate_secret(32)
    assert len(s) == 32


def test_generate_secret_too_short():
    with pytest.raises(ValueError):
        generate_secret(8)


#cert


def test_cert_info_invalid():
    with pytest.raises(ValueError):
        cert_info("not a cert")


#CLI


def test_cli_jwt_encode():
    r = runner.invoke(
        app, ["security", "jwt-encode", '{"sub":"ali"}', "-s", "mysecret"]
    )
    assert r.exit_code == 0
    assert r.stdout.count(".") >= 2


def test_cli_jwt_decode():
    token = jwt_encode({"sub": "ali"}, "mysecret")
    r = runner.invoke(app, ["security", "jwt-decode", token, "-s", "mysecret"])
    assert r.exit_code == 0
    assert "ali" in r.stdout


def test_cli_jwt_encode_invalid_json():
    r = runner.invoke(app, ["security", "jwt-encode", "not-json", "-s", "s"])
    assert r.exit_code == 1


def test_cli_encrypt():
    r = runner.invoke(app, ["security", "encrypt", "hello", "-k", "key"])
    assert r.exit_code == 0


def test_cli_decrypt():
    encoded = xor_encrypt("hello", "key")
    r = runner.invoke(app, ["security", "decrypt", encoded, "-k", "key"])
    assert r.exit_code == 0
    assert "hello" in r.stdout


def test_cli_secret():
    r = runner.invoke(app, ["security", "secret", "-l", "32"])
    assert r.exit_code == 0


def test_cli_cert_info_missing():
    r = runner.invoke(app, ["security", "cert-info", "no-file.pem"])
    assert r.exit_code == 1