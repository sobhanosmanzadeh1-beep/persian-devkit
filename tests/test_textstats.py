"""تست‌های Batch 9 — آمار متن پیشرفته."""
from __future__ import annotations

from pathlib import Path

from typer.testing import CliRunner

from persian_devkit.main import app
from persian_devkit.utils.textstats_utils import (
    PERSIAN_STOPWORDS,
    extract_emails,
    extract_hashtags,
    extract_ips,
    extract_mentions,
    extract_numbers,
    extract_urls,
    remove_stopwords,
    text_info,
    unique_words,
    word_frequency,
    word_frequency_no_stop,
)

runner = CliRunner()


#text_info


def test_text_info_basic():
    info = text_info("یک متن نمونه")
    assert info["words"] == 3
    assert info["lines"] == 1


def test_text_info_multi_line():
    info = text_info("خط اول\nخط دوم\nخط سوم")
    assert info["lines"] == 3


def test_text_info_paragraphs():
    info = text_info("پاراگراف اول\n\nپاراگراف دوم\n\nپاراگراف سوم")
    assert info["paragraphs"] == 3


def test_text_info_sentences():
    info = text_info("جمله اول. جمله دوم؟ جمله سوم!")
    assert info["sentences"] == 3


#word_frequency


def test_word_frequency_basic():
    text = "سلام سلام دنیا دنیا دنیا"
    freq = word_frequency(text, top=5)
    assert freq[0] == ("دنیا", 3)
    assert freq[1] == ("سلام", 2)


def test_word_frequency_no_stop():
    text = "و در به از که این را با سلام سلام"
    freq = word_frequency_no_stop(text, top=5, min_length=2)
    # «سلام» پرتکرارترین کلمهٔ غیر stopword است
    words = [w for w, _ in freq]
    assert "سلام" in words
    assert "و" not in words


#extract functions


def test_extract_emails():
    text = "تماس: ali@example.com یا sara@test.ir"
    emails = extract_emails(text)
    assert "ali@example.com" in emails
    assert "sara@test.ir" in emails


def test_extract_emails_unique():
    text = "a@b.com a@b.com c@d.com"
    assert len(extract_emails(text)) == 2


def test_extract_urls():
    text = "به https://github.com و www.example.com سر بزن"
    urls = extract_urls(text)
    assert any("github.com" in u for u in urls)
    assert any("example.com" in u for u in urls)


def test_extract_numbers():
    text = "من 25 سال دارم و در سال 1403 هستیم. 3.14 هم عدد پی است."
    nums = extract_numbers(text)
    assert "25" in nums
    assert "1403" in nums
    assert "3.14" in nums


def test_extract_hashtags():
    text = "این #پایتون و #برنامه_نویسی است"
    tags = extract_hashtags(text)
    assert "#پایتون" in tags
    assert "#برنامه_نویسی" in tags


def test_extract_mentions():
    text = "سلام @ali و @sara_2024"
    mentions = extract_mentions(text)
    assert "@ali" in mentions
    assert "@sara_2024" in mentions


def test_extract_ips():
    text = "سرورها: 192.168.1.1 و 10.0.0.1 و 8.8.8.8"
    ips = extract_ips(text)
    assert "192.168.1.1" in ips
    assert "8.8.8.8" in ips


#stopwords


def test_remove_stopwords():
    text = "من و تو در این خانه هستیم"
    result = remove_stopwords(text)
    assert "خانه" in result
    assert "هستیم" in result
    # «و» و «در» باید حذف شوند
    assert " و " not in f" {result} "


def test_stopwords_is_set():
    assert isinstance(PERSIAN_STOPWORDS, set)
    assert "و" in PERSIAN_STOPWORDS
    assert len(PERSIAN_STOPWORDS) > 30


#unique_words


def test_unique_words():
    words = unique_words("سلام سلام دنیا دنیا hello Hello")
    # case-insensitive
    assert words.count("سلام") == 1
    assert words.count("دنیا") == 1
    # hello و Hello یکی حساب می‌شوند
    assert len([w for w in words if w.lower() == "hello"]) == 1


#CLI


def test_cli_count_all(tmp_path: Path):
    p = tmp_path / "f.txt"
    p.write_text("سلام دنیا\nاین یک متن است", encoding="utf-8")
    r = runner.invoke(app, ["count", "all", "-f", str(p)])
    assert r.exit_code == 0
    assert "خطوط" in r.stdout
    assert "کلمات" in r.stdout


def test_cli_count_lines(tmp_path: Path):
    p = tmp_path / "f.txt"
    p.write_text("a\nb\nc", encoding="utf-8")
    r = runner.invoke(app, ["count", "lines", "-f", str(p)])
    assert r.exit_code == 0
    assert "3" in r.stdout


def test_cli_count_words(tmp_path: Path):
    p = tmp_path / "f.txt"
    p.write_text("یک دو سه چهار", encoding="utf-8")
    r = runner.invoke(app, ["count", "words", "-f", str(p)])
    assert r.exit_code == 0
    assert "4" in r.stdout


def test_cli_count_missing_file():
    r = runner.invoke(app, ["count", "lines", "-f", "no-file.txt"])
    assert r.exit_code == 1


def test_cli_frequency_words(tmp_path: Path):
    p = tmp_path / "f.txt"
    p.write_text("سلام سلام دنیا دنیا دنیا", encoding="utf-8")
    r = runner.invoke(app, ["frequency", "words", "-f", str(p)])
    assert r.exit_code == 0
    assert "دنیا" in r.stdout


def test_cli_frequency_stopwords():
    r = runner.invoke(app, ["frequency", "stopwords"])
    assert r.exit_code == 0
    assert "و" in r.stdout


def test_cli_uniq_lines(tmp_path: Path):
    p = tmp_path / "f.txt"
    p.write_text("a\nb\na\nc\nb", encoding="utf-8")
    r = runner.invoke(app, ["uniq", "lines", "-f", str(p)])
    assert r.exit_code == 0
    lines = [ln.strip() for ln in r.stdout.strip().splitlines() if ln.strip()]
    assert len(lines) == 3


def test_cli_extract_email():
    r = runner.invoke(app, ["extract", "email", "ali@example.com و sara@test.ir"])
    assert r.exit_code == 0
    assert "ali@example.com" in r.stdout


def test_cli_extract_url():
    r = runner.invoke(app, ["extract", "url", "به https://github.com سر بزن"])
    assert r.exit_code == 0
    assert "github.com" in r.stdout


def test_cli_extract_all():
    text = "ali@example.com به https://github.com و #پایتون"
    r = runner.invoke(app, ["extract", "all", text])
    assert r.exit_code == 0
    assert "ایمیل" in r.stdout
    assert "URL" in r.stdout