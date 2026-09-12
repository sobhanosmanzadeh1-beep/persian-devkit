"""تست‌های Batch 15 — رسانه (PDF و Audio)."""
from __future__ import annotations

from pathlib import Path

import pytest
from typer.testing import CliRunner

from persian_devkit.main import app
from persian_devkit.utils.pdf_utils import (
    extract_text,
    merge_pdfs,
    pdf_info,
    split_pdf,
)

runner = CliRunner()


def _make_pdf(path: Path, text: str = "Hello", pages: int = 1) -> None:
    """ساخت PDF تستی با pypdf."""
    from pypdf import PdfWriter

    writer = PdfWriter()
    for _ in range(pages):
        writer.add_blank_page(width=200, height=200)
    with path.open("wb") as f:
        writer.write(f)


#PDF


def test_pdf_info(tmp_path: Path):
    p = tmp_path / "a.pdf"
    _make_pdf(p, pages=3)
    info = pdf_info(p)
    assert info["pages"] == 3
    assert info["size_bytes"] > 0


def test_pdf_info_missing():
    with pytest.raises(ValueError):
        pdf_info(Path("no-file.pdf"))


def test_pdf_merge(tmp_path: Path):
    a = tmp_path / "a.pdf"
    b = tmp_path / "b.pdf"
    out = tmp_path / "merged.pdf"
    _make_pdf(a, pages=2)
    _make_pdf(b, pages=3)
    total = merge_pdfs([a, b], out)
    assert total == 5
    assert out.exists()


def test_pdf_merge_one_file(tmp_path: Path):
    a = tmp_path / "a.pdf"
    _make_pdf(a, pages=1)
    with pytest.raises(ValueError):
        merge_pdfs([a], tmp_path / "out.pdf")


def test_pdf_split(tmp_path: Path):
    a = tmp_path / "a.pdf"
    out = tmp_path / "part.pdf"
    _make_pdf(a, pages=5)
    count = split_pdf(a, out, start=2, end=4)
    assert count == 3
    assert out.exists()


def test_pdf_split_invalid_range(tmp_path: Path):
    a = tmp_path / "a.pdf"
    _make_pdf(a, pages=3)
    with pytest.raises(ValueError):
        split_pdf(a, tmp_path / "out.pdf", start=1, end=10)


def test_pdf_extract_text_empty(tmp_path: Path):
    # صفحهٔ خالی متن ندارد
    a = tmp_path / "a.pdf"
    _make_pdf(a, pages=1)
    text = extract_text(a)
    assert text == ""


def test_pdf_extract_text_invalid_page(tmp_path: Path):
    a = tmp_path / "a.pdf"
    _make_pdf(a, pages=2)
    with pytest.raises(ValueError):
        extract_text(a, start=5)


#CLI PDF


def test_cli_pdf_info(tmp_path: Path):
    p = tmp_path / "a.pdf"
    _make_pdf(p, pages=2)
    r = runner.invoke(app, ["pdf", "info", str(p)])
    assert r.exit_code == 0
    assert "2" in r.stdout


def test_cli_pdf_info_missing():
    r = runner.invoke(app, ["pdf", "info", "no.pdf"])
    assert r.exit_code == 1


def test_cli_pdf_pages(tmp_path: Path):
    p = tmp_path / "a.pdf"
    _make_pdf(p, pages=4)
    r = runner.invoke(app, ["pdf", "pages", str(p)])
    assert r.exit_code == 0
    assert "4" in r.stdout


def test_cli_pdf_merge(tmp_path: Path):
    a = tmp_path / "a.pdf"
    b = tmp_path / "b.pdf"
    _make_pdf(a, pages=1)
    _make_pdf(b, pages=2)
    out = tmp_path / "merged.pdf"
    r = runner.invoke(app, ["pdf", "merge", str(a), str(b), "-o", str(out)])
    assert r.exit_code == 0
    assert out.exists()


def test_cli_pdf_merge_exists(tmp_path: Path):
    a = tmp_path / "a.pdf"
    b = tmp_path / "b.pdf"
    out = tmp_path / "merged.pdf"
    _make_pdf(a, pages=1)
    _make_pdf(b, pages=1)
    out.write_bytes(b"old")
    r = runner.invoke(app, ["pdf", "merge", str(a), str(b), "-o", str(out)])
    assert r.exit_code == 1


def test_cli_pdf_split(tmp_path: Path):
    a = tmp_path / "a.pdf"
    out = tmp_path / "part.pdf"
    _make_pdf(a, pages=5)
    r = runner.invoke(
        app, ["pdf", "split", str(a), "-o", str(out), "-s", "2", "-e", "3"]
    )
    assert r.exit_code == 0
    assert out.exists()


#Audio


def test_audio_info_missing():
    from persian_devkit.utils.audio_utils import _HAS_MUTAGEN, audio_info

    if not _HAS_MUTAGEN:
        return
    with pytest.raises(ValueError):
        audio_info(Path("no-file.mp3"))


def test_audio_invalid_file(tmp_path: Path):
    from persian_devkit.utils.audio_utils import _HAS_MUTAGEN, audio_info

    if not _HAS_MUTAGEN:
        return
    p = tmp_path / "not-audio.mp3"
    p.write_bytes(b"this is not audio")
    with pytest.raises(ValueError):
        audio_info(p)


#CLI Audio


def test_cli_audio_missing():
    r = runner.invoke(app, ["audio", "info", "no-file.mp3"])
    assert r.exit_code == 1


def test_cli_audio_tags_missing():
    r = runner.invoke(app, ["audio", "tags", "no-file.mp3"])
    assert r.exit_code == 1