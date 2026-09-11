"""تست‌های base64، hash، password، nanoid، random."""
import pytest

from persian_devkit.utils.crypto_utils import (
    b64_decode,
    b64_encode,
    generate_password,
    hash_file,
    hash_text,
    nanoid,
    password_strength,
)


#base64


def test_b64_roundtrip_ascii():
    assert b64_decode(b64_encode("hello")) == "hello"


def test_b64_roundtrip_persian():
    text = "سلام دنیا"
    assert b64_decode(b64_encode(text)) == text


def test_b64_url_safe():
    text = "hello?world/friend"
    encoded = b64_encode(text, url_safe=True)
    assert "+" not in encoded and "/" not in encoded
    assert b64_decode(encoded, url_safe=True) == text


def test_b64_invalid():
    with pytest.raises(ValueError):
        b64_decode("!!!not-base64!!!")


# hash


def test_hash_text_sha256():
    # sha256("hello") معروف
    result = hash_text("hello", "sha256")
    assert result == (
        "2cf24dba5fb0a30e26e83b2ac5b9e29e1b161e5c1fa7425e73043362938b9824"
    )


def test_hash_text_md5():
    assert hash_text("", "md5") == "d41d8cd98f00b204e9800998ecf8427e"


def test_hash_text_persian():
    result = hash_text("سلام", "sha256")
    assert len(result) == 64


def test_hash_text_invalid_algo():
    with pytest.raises(ValueError):
        hash_text("x", "not-a-real-algo")


def test_hash_file(tmp_path):
    p = tmp_path / "f.txt"
    p.write_bytes(b"hello")
    assert hash_file(p, "sha256") == hash_text("hello", "sha256")


#password


def test_generate_password_length():
    pw = generate_password(length=20)
    assert len(pw) == 20


def test_generate_password_requires_pool():
    with pytest.raises(ValueError):
        generate_password(
            length=10,
            use_lower=False,
            use_upper=False,
            use_digits=False,
            use_symbols=False,
        )


def test_generate_password_too_short():
    with pytest.raises(ValueError):
        generate_password(length=2, use_lower=True, use_upper=True)


def test_password_strength_empty():
    assert password_strength("")["score"] == 0


def test_password_strength_weak():
    r = password_strength("abc")
    assert r["score"] < 40


def test_password_strength_strong():
    r = password_strength("Xy9!pQ2#mN8$kL4@")
    assert r["score"] >= 80


#nanoid


def test_nanoid_length():
    assert len(nanoid(10)) == 10
    assert len(nanoid()) == 21


def test_nanoid_unique():
    ids = {nanoid(16) for _ in range(50)}
    assert len(ids) == 50


def test_nanoid_invalid_length():
    with pytest.raises(ValueError):
        nanoid(0)