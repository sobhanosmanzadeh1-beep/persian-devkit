"""تبدیل و پردازش رنگ‌ها."""
from __future__ import annotations

import colorsys
import re
import secrets

_HEX_RE = re.compile(r"^#?([0-9a-fA-F]{3}|[0-9a-fA-F]{6})$")
_RGB_FUNC_RE = re.compile(r"^rgba?\(\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)")
_RGB_TRIPLE_RE = re.compile(r"^\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*$")

RGBTuple = tuple[int, int, int]


def parse_color(value: str) -> RGBTuple:
    """تشخیص خودکار فرمت رنگ و برگرداندن (r, g, b).

    فرمت‌های پشتیبانی‌شده: #fff, #ffffff, ff0000, rgb(255,0,0), 255,0,0
    """
    v = value.strip()

    m = _HEX_RE.match(v)
    if m:
        h = m.group(1)
        if len(h) == 3:
            h = "".join(c * 2 for c in h)
        return (int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16))

    m = _RGB_FUNC_RE.match(v)
    if m:
        return (int(m.group(1)), int(m.group(2)), int(m.group(3)))

    m = _RGB_TRIPLE_RE.match(v)
    if m:
        return (int(m.group(1)), int(m.group(2)), int(m.group(3)))

    raise ValueError(f"فرمت رنگ نامعتبر: {value}")


def rgb_to_hex(rgb: RGBTuple) -> str:
    """تبدیل (r, g, b) به #rrggbb."""
    return f"#{rgb[0]:02x}{rgb[1]:02x}{rgb[2]:02x}"


def hex_to_rgb(hex_str: str) -> RGBTuple:
    """تبدیل #rrggbb یا #rgb به (r, g, b)."""
    return parse_color(hex_str)


def rgb_to_hsl(rgb: RGBTuple) -> tuple[float, float, float]:
    """تبدیل RGB به HSL (h درجه ۰-۳۶۰، s و l در بازهٔ ۰-۱)."""
    r, g, b = (c / 255 for c in rgb)
    h, l, s = colorsys.rgb_to_hls(r, g, b)
    return (h * 360, s, l)


def hsl_to_rgb(h: float, s: float, l: float) -> RGBTuple:
    """تبدیل HSL به RGB."""
    r, g, b = colorsys.hls_to_rgb(h / 360, l, s)
    return (round(r * 255), round(g * 255), round(b * 255))


def random_color() -> RGBTuple:
    """رنگ کاملاً تصادفی."""
    return (secrets.randbelow(256), secrets.randbelow(256), secrets.randbelow(256))


def pleasant_color() -> RGBTuple:
    """رنگ تصادفی با اشباع و روشنایی دلپذیر."""
    h = secrets.randbelow(360)
    s = 0.5 + secrets.randbelow(40) / 100
    l = 0.4 + secrets.randbelow(30) / 100
    return hsl_to_rgb(h, s, l)


def generate_palette(rgb: RGBTuple, count: int = 5) -> list[RGBTuple]:
    """تولید پالت از رنگ پایه (از تیره به روشن)."""
    if count < 2:
        return [rgb]
    h, s, _ = rgb_to_hsl(rgb)
    palette: list[RGBTuple] = []
    for i in range(count):
        new_l = 0.15 + (0.70 * i / (count - 1))
        palette.append(hsl_to_rgb(h, s, new_l))
    return palette


def complementary(rgb: RGBTuple) -> RGBTuple:
    """رنگ مکمل (۱۸۰ درجه چرخش hue)."""
    h, s, l = rgb_to_hsl(rgb)
    return hsl_to_rgb((h + 180) % 360, s, l)


def luminance(rgb: RGBTuple) -> float:
    """روشنایی نسبی (۰-۱) طبق فرمول WCAG."""
    def channel(c: int) -> float:
        v = c / 255
        return v / 12.92 if v <= 0.03928 else ((v + 0.055) / 1.055) ** 2.4

    return 0.2126 * channel(rgb[0]) + 0.7152 * channel(rgb[1]) + 0.0722 * channel(rgb[2])


def contrast_ratio(a: RGBTuple, b: RGBTuple) -> float:
    """نسبت کنتراست WCAG بین دو رنگ (۱ تا ۲۱)."""
    la, lb = luminance(a), luminance(b)
    lighter, darker = max(la, lb), min(la, lb)
    return (lighter + 0.05) / (darker + 0.05)


def best_text_color(bg: RGBTuple) -> str:
    """بهترین رنگ متن (سیاه یا سفید) برای پس‌زمینه."""
    return "black" if luminance(bg) > 0.5 else "white"