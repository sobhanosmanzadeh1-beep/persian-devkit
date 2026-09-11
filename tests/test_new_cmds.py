"""تست‌های CLI برای دستورات جدید (base64, hash, password, random)."""
from pathlib import Path

from typer.testing import CliRunner

from persian_devkit.main import app

runner = CliRunner()


#base64


def test_cli_b64_encode():
    r = runner.invoke(app, ["base64", "encode", "hello"])
    assert r.exit_code == 0
    assert "aGVsbG8=" in r.stdout


def test_cli_b64_decode():
    r = runner.invoke(app, ["base64", "decode", "aGVsbG8="])
    assert r.exit_code == 0
    assert "hello" in r.stdout


def test_cli_b64_decode_invalid():
    r = runner.invoke(app, ["base64", "decode", "!!!"])
    assert r.exit_code == 1


def test_cli_b64_encode_stdin():
    r = runner.invoke(app, ["base64", "encode"], input="سلام")
    assert r.exit_code == 0


#hash


def test_cli_hash_text_sha256():
    r = runner.invoke(app, ["hash", "text", "hello"])
    assert r.exit_code == 0
    assert "2cf24dba" in r.stdout


def test_cli_hash_text_md5():
    r = runner.invoke(app, ["hash", "text", "hello", "-a", "md5"])
    assert r.exit_code == 0
    assert "5d41402a" in r.stdout


def test_cli_hash_file(tmp_path: Path):
    p = tmp_path / "f.bin"
    p.write_bytes(b"hello")
    r = runner.invoke(app, ["hash", "file", str(p)])
    assert r.exit_code == 0
    assert "2cf24dba" in r.stdout


def test_cli_hash_file_missing():
    r = runner.invoke(app, ["hash", "file", "no-such-file"])
    assert r.exit_code == 1


def test_cli_hash_all():
    r = runner.invoke(app, ["hash", "all", "hello"])
    assert r.exit_code == 0
    assert "sha256" in r.stdout
    assert "md5" in r.stdout


# password


def test_cli_password_new():
    r = runner.invoke(app, ["password", "new", "-l", "20"])
    assert r.exit_code == 0
    line = r.stdout.strip().splitlines()[-1]
    assert len(line) == 20


def test_cli_password_new_count():
    r = runner.invoke(app, ["password", "new", "-c", "3"])
    assert r.exit_code == 0
    lines = [ln for ln in r.stdout.strip().splitlines() if ln]
    assert len(lines) == 3


def test_cli_password_check():
    r = runner.invoke(app, ["password", "check", "Xy9!pQ2#mN8$kL4@"])
    assert r.exit_code == 0
    assert "قدرت" in r.stdout


#random


def test_cli_random_int():
    r = runner.invoke(app, ["random", "int", "1", "1"])
    assert r.exit_code == 0
    assert "1" in r.stdout


def test_cli_random_int_invalid():
    r = runner.invoke(app, ["random", "int", "10", "1"])
    assert r.exit_code == 1


def test_cli_random_str():
    r = runner.invoke(app, ["random", "str", "-l", "8"])
    assert r.exit_code == 0
    line = r.stdout.strip().splitlines()[-1]
    assert len(line) == 8


def test_cli_random_str_hex():
    r = runner.invoke(app, ["random", "str", "-a", "hex", "-l", "16"])
    assert r.exit_code == 0
    line = r.stdout.strip().splitlines()[-1]
    assert all(c in "0123456789abcdef" for c in line)


def test_cli_random_choice():
    r = runner.invoke(app, ["random", "choice", "a", "b", "c", "-c", "1"])
    assert r.exit_code == 0
    line = r.stdout.strip().splitlines()[-1]
    assert line in {"a", "b", "c"}


def test_cli_random_coin():
    r = runner.invoke(app, ["random", "coin"])
    assert r.exit_code == 0
    assert r.stdout.strip().splitlines()[-1] in {"شیر", "خط"}


def test_cli_random_dice():
    r = runner.invoke(app, ["random", "dice", "-s", "2"])
    assert r.exit_code == 0
    line = r.stdout.strip().splitlines()[-1]
    assert line in {"1", "2"}


def test_cli_random_dice_invalid_sides():
    r = runner.invoke(app, ["random", "dice", "-s", "1"])
    assert r.exit_code != 0


def test_cli_random_nanoid():
    r = runner.invoke(app, ["random", "nanoid", "-l", "12"])
    assert r.exit_code == 0
    line = r.stdout.strip().splitlines()[-1]
    assert len(line) == 12