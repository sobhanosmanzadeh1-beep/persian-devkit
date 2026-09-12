"""تست‌های Batch 13 — فارسی پیشرفته ۲."""
from __future__ import annotations

from typer.testing import CliRunner

from persian_devkit.main import app
from persian_devkit.utils.persian_utils import (
    add_kashida,
    char_info,
    fix_prefixes,
    fix_spacing,
    fix_suffixes,
    has_hamza,
    is_persian_char,
    justify_line,
    normalize_hamza,
    remove_kashida,
    text_to_visual,
)

runner = CliRunner()


#hamza


def test_normalize_hamza_alef():
    assert normalize_hamza("أحمد") == "احمد"


def test_normalize_hamza_hamza_below():
    assert normalize_hamza("إمام") == "امام"


def test_normalize_hamza_waw():
    assert normalize_hamza("مؤمن") == "مومن"


def test_normalize_hamza_yeh():
    assert normalize_hamza("مسئله") == "مسیله"  # ئ → ی


def test_normalize_hamza_aa_kept():
    assert normalize_hamza("آب") == "آب"


def test_normalize_hamza_aa_removed():
    assert normalize_hamza("آب", keep_aa=False) == "اب"


def test_has_hamza_true():
    assert has_hamza("أحمد") is True


def test_has_hamza_false():
    assert has_hamza("احمد") is False


#kashida


def test_add_kashida_basic():
    result = add_kashida("کتاب", 6)
    assert len(result) >= len("کتاب")
    assert "\u0640" in result


def test_add_kashida_no_change():
    assert add_kashida("کتاب", 4) == "کتاب"


def test_remove_kashida():
    text = "کـتـاب"
    assert remove_kashida(text) == "کتاب"


def test_justify_line():
    result = justify_line("این یک متن است", 20)
    assert len(result) >= 15


def test_justify_line_short():
    result = justify_line("سلام", 4)
    assert result == "سلام"


#prefix/suffix


def test_fix_prefix_mi():
    assert fix_prefixes("میروم") == "می\u200cروم"


def test_fix_prefix_nemi():
    assert fix_prefixes("نمیدانم") == "نمی\u200cدانم"


def test_fix_prefix_not_in_middle():
    result = fix_prefixes("میلیون")
    # «می» در میان کلمه نباید تبدیل شود
    assert "میلیون" == result


def test_fix_suffix_ha():
    assert fix_suffixes("کتابها") == "کتاب\u200cها"


def test_fix_suffix_tar():
    assert fix_suffixes("بزرگتر") == "بزرگ\u200cتر"


def test_fix_spacing_combined():
    result = fix_spacing("میروم کتابها")
    assert "می\u200cروم" in result
    assert "کتاب\u200cها" in result


#charinfo


def test_char_info_persian():
    info = char_info("ا")
    assert info["is_persian"] is True
    assert info["code_point"] == "U+0627"


def test_char_info_zwnj():
    info = char_info("\u200c")
    assert info["is_zwnj"] is True
    assert info["code_point"] == "U+200C"


def test_char_info_kashida():
    info = char_info("\u0640")
    assert info["is_kashida"] is True


def test_char_info_invalid():
    import pytest

    with pytest.raises(ValueError):
        char_info("abc")


def test_is_persian_char():
    assert is_persian_char("س") is True
    assert is_persian_char("a") is False


#bidi


def test_text_to_visual_basic():
    result = text_to_visual("سلام")
    assert isinstance(result, str)
    assert len(result) > 0


#CLI


def test_cli_fa_hamza():
    r = runner.invoke(app, ["fa", "hamza", "أحمد"])
    assert r.exit_code == 0
    assert "احمد" in r.stdout


def test_cli_fa_kashida():
    r = runner.invoke(app, ["fa", "kashida", "کتاب"])
    assert r.exit_code == 0


def test_cli_fa_kashida_width():
    r = runner.invoke(app, ["fa", "kashida", "کتاب", "-w", "10"])
    assert r.exit_code == 0


def test_cli_fa_kashida_remove():
    r = runner.invoke(app, ["fa", "kashida", "کـتـاب", "--remove"])
    assert r.exit_code == 0
    assert "کتاب" in r.stdout


def test_cli_fa_pish():
    r = runner.invoke(app, ["fa", "pish", "میروم"])
    assert r.exit_code == 0
    assert "می\u200cروم" in r.stdout


def test_cli_fa_suffix():
    r = runner.invoke(app, ["fa", "suffix", "کتابها"])
    assert r.exit_code == 0
    assert "کتاب\u200cها" in r.stdout


def test_cli_fa_fix():
    r = runner.invoke(app, ["fa", "fix", "میروم"])
    assert r.exit_code == 0


def test_cli_fa_charinfo():
    r = runner.invoke(app, ["fa", "charinfo", "ا"])
    assert r.exit_code == 0
    assert "U+0627" in r.stdout


def test_cli_fa_charinfo_invalid():
    r = runner.invoke(app, ["fa", "charinfo", "abc"])
    assert r.exit_code == 1


def test_cli_fa_charmap():
    r = runner.invoke(app, ["fa", "charmap", "سلام"])
    assert r.exit_code == 0


def test_cli_fa_alphabet():
    r = runner.invoke(app, ["fa", "alphabet"])
    assert r.exit_code == 0
    assert "ا" in r.stdout


def test_cli_fa_bidi():
    r = runner.invoke(app, ["fa", "bidi", "سلام"])
    assert r.exit_code == 0


def test_cli_fa_bidi_invalid_base():
    r = runner.invoke(app, ["fa", "bidi", "سلام", "-b", "X"])
    assert r.exit_code == 1