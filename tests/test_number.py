"""تست‌های مربوط به اعداد."""
from persian_devkit.utils.number_utils import (
    format_thousands,
    number_to_words,
    to_english_digits,
    to_persian_digits,
)


def test_to_persian_digits():
    assert to_persian_digits("1234567") == "۱۲۳۴۵۶۷"


def test_to_english_digits_persian():
    assert to_english_digits("۱۲۳۴۵۶۷") == "1234567"


def test_to_english_digits_arabic():
    assert to_english_digits("١٢٣") == "123"


def test_to_english_digits_mixed():
    assert to_english_digits("سلام ۱۲۳ abc") == "سلام 123 abc"


def test_format_thousands():
    assert format_thousands(1234567) == "1,234,567"
    assert format_thousands(0) == "0"
    assert format_thousands(-1000) == "-1,000"


def test_number_to_words_zero():
    assert number_to_words(0) == "صفر"


def test_number_to_words_simple():
    assert number_to_words(5) == "پنج"
    assert number_to_words(9) == "نه"


def test_number_to_words_teens():
    assert number_to_words(15) == "پانزده"
    assert number_to_words(11) == "یازده"


def test_number_to_words_tens():
    assert number_to_words(20) == "بیست"
    assert number_to_words(45) == "چهل و پنج"


def test_number_to_words_hundreds():
    assert number_to_words(200) == "دویست"
    assert number_to_words(1234) == "یک هزار و دویست و سی و چهار"


def test_number_to_words_million():
    result = number_to_words(1_234_567)
    assert "یک میلیون" in result
    assert "دویست و سی و چهار هزار" in result


def test_number_to_words_negative():
    assert number_to_words(-3) == "منفی سه"