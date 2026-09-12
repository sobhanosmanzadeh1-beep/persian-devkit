"""تست‌های Batch 8 — شبکه."""
from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest
from typer.testing import CliRunner

from persian_devkit.main import app
from persian_devkit.utils.network_utils import (
    get_hostname,
    get_local_ip,
    is_port_open,
    resolve_hostname,
)

runner = CliRunner()


#utils


def test_get_hostname():
    h = get_hostname()
    assert isinstance(h, str) and len(h) > 0


def test_get_local_ip():
    ip = get_local_ip()
    # باید IP معتبر باشد
    parts = ip.split(".")
    assert len(parts) == 4
    assert all(0 <= int(p) <= 255 for p in parts)


def test_resolve_localhost():
    ip = resolve_hostname("localhost")
    assert ip in ("127.0.0.1", "::1")


def test_resolve_invalid():
    with pytest.raises(ValueError):
        resolve_hostname("this-domain-definitely-does-not-exist-12345.com")


def test_is_port_open_invalid_host():
    # هاست نامعتبر → False (بدون exception)
    assert is_port_open("256.256.256.256", 80, timeout=0.5) is False


#CLI ip


def test_cli_ip_local():
    r = runner.invoke(app, ["ip", "local"])
    assert r.exit_code == 0
    assert "." in r.stdout  # احتمالاً IP


def test_cli_ip_info_no_public():
    r = runner.invoke(app, ["ip", "info", "--no-public"])
    assert r.exit_code == 0
    assert "Hostname" in r.stdout


def test_cli_ip_resolve():
    r = runner.invoke(app, ["ip", "resolve", "localhost"])
    assert r.exit_code == 0
    assert "127.0.0.1" in r.stdout or "::1" in r.stdout


def test_cli_ip_resolve_invalid():
    r = runner.invoke(app, ["ip", "resolve", "invalid-xyz-9999.com"])
    assert r.exit_code == 1


#CLI dns


def test_cli_dns_lookup_a():
    r = runner.invoke(app, ["dns", "lookup", "localhost", "-t", "A"])
    assert r.exit_code == 0


def test_cli_dns_lookup_invalid_type():
    r = runner.invoke(app, ["dns", "lookup", "example.com", "-t", "XYZ"])
    assert r.exit_code == 1


def test_cli_dns_all_invalid():
    r = runner.invoke(app, ["dns", "all", "this-domain-does-not-exist-99999.com"])
    # احتمالاً هیچ رکوردی نیست → پیام warning
    assert r.exit_code == 0 or r.exit_code == 1


#CLI port


def test_cli_port_check_invalid_range():
    r = runner.invoke(app, ["port", "check", "localhost", "70000"])
    assert r.exit_code != 0


def test_cli_port_scan_invalid_range():
    r = runner.invoke(app, ["port", "scan", "localhost", "100", "50"])
    assert r.exit_code == 1


def test_cli_port_scan_too_large():
    r = runner.invoke(app, ["port", "scan", "localhost", "1", "5000"])
    assert r.exit_code == 1


#CLI ping


def test_cli_ping_invalid_host():
    r = runner.invoke(app, ["ping", "host", "invalid-xyz-9999.com", "-c", "1"])
    assert r.exit_code == 1


#CLI http


def test_cli_http_head_invalid_url():
    r = runner.invoke(app, ["http", "head", "not-a-url", "-t", "2"])
    assert r.exit_code == 1


def test_cli_http_post_invalid_json():
    r = runner.invoke(
        app, ["http", "post", "http://example.com", "-d", "{invalid}"]
    )
    assert r.exit_code == 1


#mock tests


def test_get_public_ip_with_mock(monkeypatch):
    """IP عمومی با mock."""
    import httpx
    from persian_devkit.utils import network_utils

    class FakeResponse:
        status_code = 200
        text = "1.2.3.4"

    def fake_get(*args, **kwargs):
        return FakeResponse()

    monkeypatch.setattr(httpx, "get", fake_get)
    result = network_utils.get_public_ip()
    assert result == "1.2.3.4"


def test_get_public_ip_all_fail(monkeypatch):
    """همهٔ سرویس‌ها fail → None."""
    import httpx
    from persian_devkit.utils import network_utils

    def fake_get(*args, **kwargs):
        raise httpx.ConnectError("fake")

    monkeypatch.setattr(httpx, "get", fake_get)
    assert network_utils.get_public_ip() is None


def test_is_port_open_localhost(monkeypatch):
    """تست پورت با mock."""
    from persian_devkit.utils import network_utils

    class FakeSocket:
        def __init__(self, *a, **kw):
            pass

        def settimeout(self, t):
            pass

        def connect(self, addr):
            pass

        def __enter__(self):
            return self

        def __exit__(self, *a):
            pass

    monkeypatch.setattr(network_utils.socket, "socket", FakeSocket)
    assert network_utils.is_port_open("localhost", 80) is True


def test_ping_host_not_found(monkeypatch):
    """ping وقتی دستور نصب نیست."""
    from persian_devkit.utils import network_utils
    import subprocess

    def fake_run(*a, **kw):
        raise FileNotFoundError("ping not found")

    monkeypatch.setattr(subprocess, "run", fake_run)
    result = network_utils.ping_host("localhost", count=1)
    assert result["success"] is False
    assert result["error"] == "ping-not-found"


def test_http_request_with_mock(monkeypatch):
    """HTTP request با mock کامل."""
    import httpx
    from persian_devkit.utils import http_utils

    class FakeResponse:
        status_code = 200
        reason_phrase = "OK"
        url = "http://example.com/"
        headers = {"content-type": "text/html; charset=utf-8"}
        content = b"<html>hello</html>"
        text = "<html>hello</html>"
        history: list = []

    class FakeClient:
        def __init__(self, **kw):
            pass

        def __enter__(self):
            return self

        def __exit__(self, *a):
            pass

        def request(self, method, url):
            return FakeResponse()

    monkeypatch.setattr(httpx, "Client", FakeClient)
    result = http_utils.http_request("http://example.com")
    assert result["status"] == 200
    assert result["reason"] == "OK"
    assert result["content_length"] == 18


def test_http_request_invalid_method(monkeypatch):
    """متد نامعتبر."""
    from persian_devkit.utils import http_utils

    try:
        http_utils.http_request("http://example.com", method="INVALID")
        assert False, "باید ValueError می‌داد"
    except ValueError as e:
        assert "INVALID" in str(e)


def test_dns_lookup_mx_no_dnspython(monkeypatch):
    """lookup MX بدون dnspython."""
    from persian_devkit.utils import dns_utils

    monkeypatch.setattr(dns_utils, "_HAS_DNSPYTHON", False)
    try:
        dns_utils.lookup("example.com", "MX")
        assert False, "باید ValueError می‌داد"
    except ValueError as e:
        assert "dnspython" in str(e)


def test_cli_http_get_mock(monkeypatch):
    """CLI http get با mock."""
    import httpx
    from typer.testing import CliRunner
    from persian_devkit.main import app as _app

    class FakeResponse:
        status_code = 200
        reason_phrase = "OK"
        url = "http://test.com/"
        headers = {"content-type": "text/plain"}
        content = b"hi"
        text = "hi"
        history: list = []

    class FakeClient:
        def __init__(self, **kw):
            pass

        def __enter__(self):
            return self

        def __exit__(self, *a):
            pass

        def request(self, method, url):
            return FakeResponse()

    monkeypatch.setattr(httpx, "Client", FakeClient)
    r = CliRunner().invoke(_app, ["http", "get", "http://test.com"])
    assert r.exit_code == 0
    assert "200" in r.stdout


def test_cli_ping_not_found(monkeypatch):
    """CLI ping وقتی ping نصب نیست."""
    import subprocess
    from typer.testing import CliRunner
    from persian_devkit.main import app as _app

    def fake_run(*a, **kw):
        raise FileNotFoundError("ping not found")

    monkeypatch.setattr(subprocess, "run", fake_run)
    r = CliRunner().invoke(_app, ["ping", "host", "localhost", "-c", "1"])
    assert r.exit_code == 1
