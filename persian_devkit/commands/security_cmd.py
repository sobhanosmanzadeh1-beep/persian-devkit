"""دستور pdev security — ابزارهای امنیتی."""
from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.syntax import Syntax
from rich.table import Table

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

app = typer.Typer(help="ابزارهای امنیتی (JWT، رمز، گواهی).", no_args_is_help=True)
console = Console()


def _fail(msg: str) -> None:
    console.print(f"[red]✗ خطا:[/red] {msg}")
    raise typer.Exit(1)


#JWT


@app.command("jwt-encode")
def jwt_encode_cmd(
    payload: str = typer.Argument(..., help="payload به شکل JSON."),
    secret: str = typer.Option(..., "--secret", "-s", prompt=True, hide_input=True),
    algorithm: str = typer.Option("HS256", "--algo", "-a", help="HS256/HS384/HS512."),
    expires_in: Optional[int] = typer.Option(
        None, "--expires-in", "-e", help="انقضا به ثانیه."
    ),
) -> None:
    """ساخت JWT امضاشده."""
    try:
        data = json.loads(payload)
    except json.JSONDecodeError as e:
        _fail(f"payload نامعتبر: {e}")

    if expires_in:
        data["exp"] = int(time.time()) + expires_in
        data.setdefault("iat", int(time.time()))

    try:
        token = jwt_encode(data, secret, algorithm=algorithm)
    except ValueError as e:
        _fail(str(e))

    console.print(token)


@app.command("jwt-decode")
def jwt_decode_cmd(
    token: str = typer.Argument(..., help="JWT برای رمزگشایی."),
    secret: Optional[str] = typer.Option(
        None, "--secret", "-s", help="کلید برای بررسی امضا (اختیاری)."
    ),
) -> None:
    """رمزگشایی JWT (و بررسی امضا اگر secret داده شود)."""
    verify = secret is not None
    try:
        payload = jwt_decode(token, secret or "", verify=verify)
    except ValueError as e:
        _fail(str(e))

    text = json.dumps(payload, ensure_ascii=False, indent=2)
    console.print(Syntax(text, "json", word_wrap=True, background_color="default"))


#XOR crypto


@app.command("encrypt")
def encrypt_cmd(
    text: str = typer.Argument(..., help="متن برای رمزگذاری."),
    key: str = typer.Option(..., "--key", "-k", prompt=True, hide_input=True),
) -> None:
    """رمزگذاری XOR (خروجی Base64)."""
    try:
        result = xor_encrypt(text, key)
    except ValueError as e:
        _fail(str(e))
    console.print(result)


@app.command("decrypt")
def decrypt_cmd(
    encoded: str = typer.Argument(..., help="متن رمزگذاری‌شده (Base64)."),
    key: str = typer.Option(..., "--key", "-k", prompt=True, hide_input=True),
) -> None:
    """رمزگشایی XOR."""
    try:
        result = xor_decrypt(encoded, key)
    except ValueError as e:
        _fail(str(e))
    console.print(result)


#password


@app.command("hash-password")
def hash_password_cmd(
    password: str = typer.Option(
        ..., "--password", "-p", prompt=True, hide_input=True, confirmation_prompt=True
    ),
) -> None:
    """هش کردن رمز عبور با PBKDF2-SHA256."""
    console.print(hash_password(password))


@app.command("verify-password")
def verify_password_cmd(
    password: str = typer.Option(
        ..., "--password", "-p", prompt=True, hide_input=True
    ),
    hashed: str = typer.Option(..., "--hash", "-H", help="هش ذخیره‌شده."),
) -> None:
    """بررسی رمز عبور با هش."""
    if verify_password(password, hashed):
        console.print("[green]✓ رمز صحیح است[/green]")
    else:
        console.print("[red]✗ رمز اشتباه است[/red]")
        raise typer.Exit(1)


#secret


@app.command("secret")
def secret_cmd(
    length: int = typer.Option(32, "--length", "-l", min=16, max=256),
    count: int = typer.Option(1, "--count", "-c", min=1, max=20),
) -> None:
    """تولید کلید امن (برای JWT secret یا متغیر محیطی)."""
    for _ in range(count):
        try:
            console.print(generate_secret(length))
        except ValueError as e:
            _fail(str(e))


#cert


@app.command("cert-info")
def cert_info_cmd(
    path: Path = typer.Argument(..., help="مسیر فایل گواهی PEM."),
) -> None:
    """اطلاعات پایهٔ گواهی PEM (فینگرپرینت، طول)."""
    if not path.exists():
        _fail(f"فایل یافت نشد: {path}")
    try:
        info = cert_info(path.read_text(encoding="utf-8"))
    except (ValueError, OSError) as e:
        _fail(str(e))

    table = Table(title=f"🔐 {path.name}", title_style="bold cyan", show_header=False)
    table.add_column("شاخص", style="bold")
    table.add_column("مقدار", style="green", overflow="fold")
    table.add_row("طول PEM", f"{info['pem_length']} بایت")
    table.add_row("طول DER", f"{info['der_length']} بایت")
    table.add_row("SHA-256", info["sha256_fingerprint"])
    table.add_row("SHA-1", info["sha1_fingerprint"])
    console.print(table)