"""تست‌های مربوط به UUID."""
import re
import uuid as uuidlib

from persian_devkit.commands.uuid_cmd import short_uuid


def test_short_uuid_length():
    assert len(short_uuid()) == 22


def test_short_uuid_unique():
    values = {short_uuid() for _ in range(50)}
    assert len(values) == 50


def test_short_uuid_charset():
    s = short_uuid()
    assert re.fullmatch(r"[A-Za-z0-9_\-]+", s)


def test_uuid4_version():
    u = uuidlib.uuid4()
    assert u.version == 4