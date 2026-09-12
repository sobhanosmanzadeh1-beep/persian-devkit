"""توابع کمکی خواندن متادیتای فایل‌های صوتی."""
from __future__ import annotations

from pathlib import Path
from typing import Optional

try:
    from mutagen import File as MutagenFile
    _HAS_MUTAGEN = True
except ImportError:
    _HAS_MUTAGEN = False


def _require_mutagen() -> None:
    if not _HAS_MUTAGEN:
        raise RuntimeError("mutagen نصب نیست: pip install mutagen")


def _open(path: Path):
    _require_mutagen()
    if not path.exists():
        raise ValueError(f"فایل یافت نشد: {path}")
    try:
        return MutagenFile(str(path))
    except Exception as exc:
        raise ValueError(f"خطا در باز کردن فایل صوتی: {exc}") from exc


def _format_duration(seconds: float) -> str:
    """قالب‌بندی خوانا برای مدت زمان."""
    total = int(seconds)
    hours, rem = divmod(total, 3600)
    minutes, secs = divmod(rem, 60)
    if hours:
        return f"{hours}:{minutes:02d}:{secs:02d}"
    return f"{minutes}:{secs:02d}"


def audio_info(path: Path) -> dict:
    """اطلاعات فایل صوتی: فرمت، مدت، بیتریت، تگ‌ها."""
    audio = _open(path)
    if audio is None:
        raise ValueError("فرمت فایل شناسایی نشد")

    info = audio.info
    result: dict = {
        "format": type(audio).__name__,
        "size_bytes": path.stat().st_size,
        "duration": getattr(info, "length", 0.0),
        "duration_fmt": _format_duration(getattr(info, "length", 0.0)),
        "bitrate": getattr(info, "bitrate", None),
        "sample_rate": getattr(info, "sample_rate", None),
        "channels": getattr(info, "channels", None),
        "tags": {},
    }

    # استخراج تگ‌ها
    if audio.tags:
        for key in audio.tags.keys():
            value = audio.tags[key]
            if isinstance(value, list):
                value = ", ".join(str(v) for v in value)
            result["tags"][str(key)] = str(value)

    return result


# نگاشت کلیدهای رایج تگ‌ها
_TAG_KEYS = {
    "title": ("TIT2", "title", "\xa9nam"),
    "artist": ("TPE1", "artist", "\xa9ART"),
    "album": ("TALB", "album", "\xa9alb"),
    "year": ("TDRC", "date", "\xa9day", "year"),
    "genre": ("TCON", "genre", "\xa9gen"),
    "track": ("TRCK", "tracknumber", "trkn"),
    "album_artist": ("TPE2", "albumartist", "aART"),
}


def audio_tags(path: Path) -> dict[str, str]:
    """تگ‌های اصلی (title, artist, album, ...)."""
    audio = _open(path)
    if audio is None or not audio.tags:
        return {}

    result: dict[str, str] = {}
    tags = audio.tags
    for friendly, keys in _TAG_KEYS.items():
        for key in keys:
            try:
                if key in tags:
                    value = tags[key]
                    if hasattr(value, "text"):
                        value = value.text
                    if isinstance(value, list):
                        value = ", ".join(str(v) for v in value)
                    result[friendly] = str(value)
                    break
            except (KeyError, TypeError):
                continue
    return result


def extract_cover(path: Path, output: Path) -> Optional[Path]:
    """استخراج تصویر جلد از فایل صوتی (اگر موجود باشد)."""
    audio = _open(path)
    if audio is None or not audio.tags:
        return None

    # APIC (MP3) یا covr (M4A)
    for key in audio.tags.keys():
        if key.startswith("APIC") or key == "covr":
            picture = audio.tags[key]
            data = None
            if isinstance(picture, list):
                picture = picture[0]
            if hasattr(picture, "data"):
                data = picture.data
            elif isinstance(picture, bytes):
                data = bytes(picture)

            if data:
                output.write_bytes(data)
                return output

    return None