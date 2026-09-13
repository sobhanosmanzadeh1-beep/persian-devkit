# Changelog

تمام تغییرات مهم این پروژه در این فایل مستند می‌شوند.

## [2.1.0] — 2026-09-13

### Added
- 🩺 `pdev doctor` — بررسی سلامت نصب و محیط با راه‌حل برای هر مشکل
- ⬆️  `pdev upgrade` — بررسی و ارتقا به آخرین نسخه
- ℹ️  `pdev info` — اطلاعات کامل pdev و سیستم
- 🏷  `pdev version` — اطلاعات دقیق نسخه

### Documentation
- `CONTRIBUTING.md` — راهنمای مشارکت
- `CODE_OF_CONDUCT.md` — قواعد رفتاری
- `SECURITY.md` — سیاست امنیتی
- Issue Templates (bug + feature)
- Pull Request Template
- `.editorconfig` و `.gitattributes`

### Stats
- ۶۶ دستور | ۶۰۷ تست | پوشش ۸۲٪

## [2.0.0] — 2026-09-12

### Added
- ✨ `pdev shell` — حالت تعاملی (REPL)
- ⚙️  `pdev config` — فایل تنظیمات در `~/.pdev/config.toml`
- 🔌 `pdev plugin` — سیستم پلاگین از `~/.pdev/plugins/`

## [1.9.0] — 2026-09-12

### Added
- 📄 `pdev pdf` — کار با PDF (info, pages, text, merge, split)
- 🎵 `pdev audio` — متادیتای فایل صوتی (info, tags, cover)

## [1.8.0] — 2026-09-12

### Added
- 🤖 `pdev auto` — خودکارسازی (run, repeat, batch, watch, cron)

## [1.7.0] — 2026-09-12

### Added
- 🇮🇷 `pdev fa` — فارسی پیشرفته ۲ (hamza, kashida, pish, suffix, charinfo, charmap, alphabet, bidi)

## [1.6.0] — 2026-09-12

### Added
- 🗄️  `pdev sqlite` — کار با SQLite
- 📊 `pdev csv-query` — کوئری SQL روی CSV

## [1.5.0] — 2026-09-12

### Added
- 🔐 `pdev security` — امنیت (JWT, PBKDF2, XOR, cert-info, secret)

## [1.4.0] — 2026-09-12

### Added
- 💻 `pdev sys` — اطلاعات سیستم (disk, memory, cpu, top, uptime, python)

## [1.3.0] — 2026-09-12

### Added
- 🔢 `pdev count`, `pdev frequency`, `pdev uniq`, `pdev extract`

## [1.2.0] — 2026-09-12

### Added
- 🌐 `pdev ip`, `pdev dns`, `pdev port`, `pdev http`, `pdev ping`

## [1.1.0] — 2026-09-12

### Added
- 📆 `pdev calendar`, 🔤 `pdev transliterate`, 🥇 `pdev numerals`, 🌙 `pdev hijri`, 📑 `pdev sort`

قالب بر اساس [Keep a Changelog](https://keepachangelog.com/fa/1.1.0/) است،
و این پروژه از [Semantic Versioning](https://semver.org/lang/fa/) تبعیت می‌کند.
## [1.0.1] — 2026-09-12

### Changed
- افزودن لینک‌های واقعی GitHub به metadata پکیج
- بهبود مستندات و لینک‌های PyPI
## [1.0.0] — 2026-09-11

### Added

#### تاریخ و اعداد
- `pdev date` — تبدیل و محاسبهٔ تاریخ شمسی/میلادی
  - `to-jalali`, `to-gregorian`, `now`, `diff`
- `pdev number` — تبدیل و قالب‌بندی اعداد
  - `to-persian`, `to-english`, `format`, `words`

#### متن
- `pdev text` — پردازش متن فارسی
  - `halfspace`, `normalize`, `reverse`, `stats`
  - `slug`, `case`, `diff`, `regex`

#### کریپتو و امنیت
- `pdev base64` — رمزگذاری/رمزگشایی (`encode`, `decode`)
- `pdev hash` — محاسبهٔ هش (`text`, `file`, `all`)
- `pdev password` — تولید و سنجش رمز (`new`, `check`)
- `pdev random` — مقادیر تصادفی (`int`, `str`, `choice`, `coin`, `dice`, `nanoid`)
- `pdev uuid` — تولید UUID (`new`, `short`)

#### داده
- `pdev json` — کار با JSON (`pretty`, `minify`, `validate`, `keys`, `flatten`)
- `pdev jq` — کوئری JSON با JSONPath ساده
- `pdev yaml` — کار با YAML (`pretty`, `validate`, `to-json`, `from-json`)
- `pdev toml` — کار با TOML (`validate`, `to-json`, `from-json`)
- `pdev csv` — کار با CSV (`show`, `to-json`, `columns`, `filter`)
- `pdev env` — مدیریت `.env` (`show`, `get`, `to-json`, `to-shell`, `sort`)

#### وب و شبکه
- `pdev url` — کار با URL (`encode`, `decode`, `parse`, `build`, `decode-query`)
- `pdev time` — timestamp و مدت زمان (`now`, `to-unix`, `from-unix`, `duration`, `ago`)

#### بصری
- `pdev color` — کار با رنگ‌ها (`convert`, `palette`, `random`, `contrast`, `complement`)
- `pdev qrcode` — تولید QR Code از متن (فارسی و انگلیسی)
- `pdev image` — اطلاعات و تبدیل تصاویر (`info`, `resize`, `convert`)

#### داده‌های نمونهٔ فارسی
- `pdev lorem` — متن نمونهٔ فارسی (`paragraph`, `sentence`, `words`, `all`)
- `pdev name` — نام و داده‌های نمونهٔ فارسی (`full`, `first`, `last`, `city`, `email`, `profile`)

#### ابزار پروژه
- `pdev license` — تولید فایل لایسنس (`list`, `show`, `new`) با ۷ لایسنس رایج
- `pdev gitignore` — تولید `.gitignore` برای ۱۳ زبان/ابزار
- `pdev scaffold` — ساخت پروژه از قالب (python, node, minimal)
- `pdev template` — رندر قالب متنی با متغیرها

### Features

- خروجی رنگی با Rich
- پیام‌های خطا به فارسی
- پشتیبانی از stdin و pipe
- Shل Completion برای bash و zsh
- گزینه‌های سراسری: `--version`, `--verbose`, `--quiet`
- ۳۱۹ تست واحد با پوشش ۹۱٪
- پشتیبانی از Python 3.10+

[1.0.0]: https://github.com/your-username/persian-devkit/releases/tag/v1.0.0