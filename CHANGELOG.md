# Changelog

تمام تغییرات مهم این پروژه در این فایل مستند می‌شوند.

قالب بر اساس [Keep a Changelog](https://keepachangelog.com/fa/1.1.0/) است،
و این پروژه از [Semantic Versioning](https://semver.org/lang/fa/) تبعیت می‌کند.

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