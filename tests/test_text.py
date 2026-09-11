"""تست‌های مربوط به پاک‌سازی و پردازش متن."""
from persian_devkit.utils.text_utils import (
    fix_halfspace,
    normalize,
    reverse_text,
    text_stats,
)


def test_fix_halfspace_prefix():
    result = fix_halfspace("می روم")
    assert "می\u200cروم" == result


def test_fix_halfspace_nemi_prefix():
    result = fix_halfspace("نمی دانم")
    assert result == "نمی\u200cدانم"


def test_fix_halfspace_suffix_ha():
    result = fix_halfspace("کتاب ها")
    assert result == "کتاب\u200cها"


def test_fix_halfspace_suffix_haye():
    result = fix_halfspace("کتاب های من")
    assert result == "کتاب\u200cهای من"


def test_normalize_arabic_yeh():
    assert "ی" in normalize("علي")
    assert "\u064a" not in normalize("علي")


def test_normalize_arabic_kaf():
    assert "ک" in normalize("كتاب")
    assert "\u0643" not in normalize("كتاب")


def test_normalize_extra_spaces():
    assert normalize("سلام  دنیا") == "سلام دنیا"
    assert normalize("سلام   دنیا   ") == "سلام دنیا"


def test_reverse_text_latin():
    assert reverse_text("abc") == "cba"


def test_reverse_text_persian():
    assert reverse_text("سلام") == "مالس"


def test_text_stats():
    s = text_stats("یک متن نمونه")
    assert s["words"] == 3
    assert s["chars"] == 12
    assert s["lines"] == 1


def test_text_stats_multi_line():
    s = text_stats("خط اول\nخط دوم\nخط سوم")
    assert s["lines"] == 3
    assert s["words"] == 6