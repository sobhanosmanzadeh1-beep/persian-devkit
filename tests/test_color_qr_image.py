"""تست‌های رنگ، QR Code و تصویر."""
from __future__ import annotations

from pathlib import Path

import pytest
from typer.testing import CliRunner

from persian_devkit.main import app
from persian_devkit.utils.color_utils import (
    best_text_color,
    complementary,
    contrast_ratio,
    generate_palette,
    hex_to_rgb,
    hsl_to_rgb,
    luminance,
    parse_color,
    pleasant_color,
    random_color,
    rgb_to_hex,
    rgb_to_hsl,
)
from persian_devkit.utils.qrcode_utils import qr_to_ascii, qr_to_image

runner = CliRunner()


#parse


def test_parse_hex_full():
    assert parse_color("#ff0000") == (255, 0, 0)


def test_parse_hex_short():
    assert parse_color("#fff") == (255, 255, 255)


def test_parse_hex_no_hash():
    assert parse_color("ff0000") == (255, 0, 0)


def test_parse_rgb_func():
    assert parse_color("rgb(10, 20, 30)") == (10, 20, 30)


def test_parse_rgb_triple():
    assert parse_color("10,20,30") == (10, 20, 30)


def test_parse_invalid():
    with pytest.raises(ValueError):
        parse_color("nope")


#hex


def test_rgb_to_hex():
    assert rgb_to_hex((255, 0, 128)) == "#ff0080"


def test_hex_roundtrip():
    rgb = (123, 45, 67)
    assert hex_to_rgb(rgb_to_hex(rgb)) == rgb


#hsl


def test_rgb_to_hsl_red():
    h, s, l = rgb_to_hsl((255, 0, 0))
    assert round(h) in (0, 360)
    assert round(s, 2) == 1.0
    assert round(l, 2) == 0.5


def test_hsl_roundtrip():
    rgb = hsl_to_rgb(210, 0.5, 0.5)
    h2, s2, l2 = rgb_to_hsl(rgb)
    assert abs(210 - h2) < 1
    assert abs(0.5 - s2) < 0.02
    assert abs(0.5 - l2) < 0.02


#random


def test_random_color_range():
    r, g, b = random_color()
    assert all(0 <= v <= 255 for v in (r, g, b))


def test_pleasant_color_range():
    r, g, b = pleasant_color()
    assert all(0 <= v <= 255 for v in (r, g, b))


#palette/complement


def test_palette_count():
    p = generate_palette((100, 150, 200), count=5)
    assert len(p) == 5


def test_palette_sorted_by_lightness():
    p = generate_palette((100, 150, 200), count=5)
    light = [luminance(c) for c in p]
    assert light == sorted(light)


def test_palette_min_count():
    p = generate_palette((100, 100, 100), count=1)
    assert len(p) == 1


def test_complementary_red():
    comp = complementary((255, 0, 0))
    assert comp[0] < 100 and comp[1] > 100 and comp[2] > 100


#contrast


def test_contrast_black_white():
    assert round(contrast_ratio((0, 0, 0), (255, 255, 255)), 1) == 21.0


def test_contrast_identical():
    assert contrast_ratio((100, 100, 100), (100, 100, 100)) == 1.0


def test_best_text_color_dark_bg():
    assert best_text_color((0, 0, 0)) == "white"


def test_best_text_color_light_bg():
    assert best_text_color((255, 255, 255)) == "black"


#QR


def test_qr_ascii_not_empty():
    art = qr_to_ascii("hello")
    assert len(art) > 0
    assert any(ch in art for ch in "█▀▄")


def test_qr_persian():
    art = qr_to_ascii("سلام دنیا")
    assert len(art) > 0


def test_qr_invalid_error():
    with pytest.raises(ValueError):
        qr_to_ascii("x", error="X")


def test_qr_image_saved(tmp_path: Path):
    out = tmp_path / "qr.png"
    qr_to_image("hello", out)
    assert out.exists() and out.stat().st_size > 0


def test_qr_ascii_non_invert():
    art = qr_to_ascii("hi", invert=False)
    assert len(art) > 0


#CLI color


def test_cli_color_convert():
    r = runner.invoke(app, ["color", "convert", "#ff0000"])
    assert r.exit_code == 0
    assert "#ff0000" in r.stdout


def test_cli_color_convert_invalid():
    r = runner.invoke(app, ["color", "convert", "nope"])
    assert r.exit_code == 1


def test_cli_color_palette():
    r = runner.invoke(app, ["color", "palette", "#ff8800"])
    assert r.exit_code == 0


def test_cli_color_random():
    r = runner.invoke(app, ["color", "random"])
    assert r.exit_code == 0


def test_cli_color_random_pleasant():
    r = runner.invoke(app, ["color", "random", "-p", "-c", "3"])
    assert r.exit_code == 0


def test_cli_color_contrast():
    r = runner.invoke(app, ["color", "contrast", "#000", "#fff"])
    assert r.exit_code == 0


def test_cli_color_contrast_invalid():
    r = runner.invoke(app, ["color", "contrast", "#000", "xyz"])
    assert r.exit_code == 1


def test_cli_color_complement():
    r = runner.invoke(app, ["color", "complement", "#ff0000"])
    assert r.exit_code == 0


#CLI qrcode


def test_cli_qrcode_terminal():
    r = runner.invoke(app, ["qrcode", "hello"])
    assert r.exit_code == 0


def test_cli_qrcode_persian():
    r = runner.invoke(app, ["qrcode", "سلام دنیا"])
    assert r.exit_code == 0


def test_cli_qrcode_file(tmp_path: Path):
    out = tmp_path / "q.png"
    r = runner.invoke(app, ["qrcode", "hello", "-o", str(out)])
    assert r.exit_code == 0
    assert out.exists()


def test_cli_qrcode_invalid_error(tmp_path: Path):
    out = tmp_path / "q.png"
    r = runner.invoke(app, ["qrcode", "hi", "-e", "X", "-o", str(out)])
    assert r.exit_code == 1


#CLI image


@pytest.fixture
def sample_image(tmp_path: Path) -> Path:
    from PIL import Image

    p = tmp_path / "test.png"
    Image.new("RGB", (100, 50), color=(255, 0, 0)).save(p)
    return p


def test_cli_image_info(sample_image: Path):
    r = runner.invoke(app, ["image", "info", str(sample_image)])
    assert r.exit_code == 0
    assert "100" in r.stdout and "50" in r.stdout


def test_cli_image_info_missing():
    r = runner.invoke(app, ["image", "info", "no-such-file.png"])
    assert r.exit_code == 1


def test_cli_image_resize(sample_image: Path, tmp_path: Path):
    out = tmp_path / "resized.png"
    r = runner.invoke(
        app, ["image", "resize", str(sample_image), "50", "-o", str(out)]
    )
    assert r.exit_code == 0
    assert out.exists()

    from PIL import Image

    with Image.open(out) as img:
        assert img.width == 50
        assert img.height == 25


def test_cli_image_resize_missing():
    r = runner.invoke(app, ["image", "resize", "no-file.png", "50"])
    assert r.exit_code == 1


def test_cli_image_convert(sample_image: Path, tmp_path: Path):
    out = tmp_path / "test.jpg"
    r = runner.invoke(app, ["image", "convert", str(sample_image), str(out)])
    assert r.exit_code == 0
    assert out.exists()


def test_cli_image_convert_missing(tmp_path: Path):
    out = tmp_path / "out.jpg"
    r = runner.invoke(app, ["image", "convert", "no-file.png", str(out)])
    assert r.exit_code == 1