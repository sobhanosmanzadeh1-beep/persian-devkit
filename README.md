# persian-devkit

> جعبه‌ابزار خط فرمان برای توسعه‌دهندگان فارسی‌زبان — تاریخ، عدد، متن، UUID و JSON در یک CLI سریع و زیبا.

[![PyPI](https://img.shields.io/badge/pypi-persian--devkit-blue)](https://pypi.org/project/persian-devkit/)
[![Python](https://img.shields.io/badge/python-3.10%2B-blue)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
![Version](https://img.shields.io/badge/version-1.0.0-blue)
![Tests](https://img.shields.io/badge/tests-319%20passing-brightgreen)
![Coverage](https://img.shields.io/badge/coverage-91%25-brightgreen)
---

##  چرا persian-devkit؟

هر توسعه‌دهندهٔ ایرانی روزانه با کارهای تکراری مثل تبدیل تاریخ شمسی، اصلاح نیم‌فاصله، تبدیل اعداد فارسی، ساخت UUID و … سروکار دارد. **pdev** همهٔ این کارها را در یک دستور ساده و یکپارچه جمع می‌کند.

-  سبک و سریع
-  خروجی رنگی با Rich
-  کار روی Linux، macOS و Windows
- تست‌شده با pytest (پوشش ۸۰٪+)
-  پشتیبانی از stdin و pipe
- شل‌کامپلیشن برای bash و zsh

---

## نصب

**نسخهٔ فعلی:** 1.0.0 — پایدار

شامل **۳۷ دستور** و **۱۱۰+ زیرفرمان** برای کارهای روزمره:
تاریخ شمسی، متن فارسی، اعداد، JSON، YAML، TOML، CSV، URL، رنگ،
QR Code، تصویر، داده‌های نمونهٔ فارسی، و ابزارهای پروژه.

```bash
pip install persian-devkit
```

یا نصب توسعه:

```bash
git clone https://github.com/your-username/persian-devkit
cd persian-devkit
pip install -e ".[dev]"
```

---

## شروع سریع

```bash
pdev --help
pdev date now
pdev number words 1234
echo "می روم" | pdev text halfspace
pdev uuid new --count 3
```

---

##  دستورات


### 🔐 `pdev base64` — رمزگذاری و رمزگشایی

```bash
$ pdev base64 encode "hello world"
aGVsbG8gd29ybGQ=

$ pdev base64 decode "aGVsbG8gd29ybGQ="
hello world

$ echo "سلام" | pdev base64 encode
2LPZhNin2YU=
```

### 🧮 `pdev hash` — محاسبهٔ هش

```bash
$ pdev hash text "hello"
2cf24dba5fb0a30e26e83b2ac5b9e29e1b161e5c1fa7425e73043362938b9824

$ pdev hash text "hello" --algo md5
5d41402abc4b2a76b9719d911017c592

$ pdev hash file myfile.zip --algo sha512
...

$ pdev hash all "hello"
┏━━━━━━━━━ 🔐 هش‌ها ━━━━━━━━━┓
┃ الگوریتم │ مقدار          ┃
┡━━━━━━━━━╇━━━━━━━━━━━━━━━┩
│ md5      │ 5d41402a...    │
│ sha1     │ aaf4c61d...    │
│ sha256   │ 2cf24dba...    │
│ ...      │ ...            │
└──────────┴────────────────┘
```

### 🔑 `pdev password` — تولید و سنجش رمز

```bash
$ pdev password new
k9$mN2#pQ8@xL4zW

$ pdev password new --length 32 --count 3
...

$ pdev password check "abc123"
┏━━━━━━━━ 🔒 قدرت رمز ━━━━━━━━┓
┃ شاخص    │ مقدار            ┃
┡━━━━━━━━━╇━━━━━━━━━━━━━━━━━┩
│ امتیاز  │ 30/100           │
│ برچسب   │ ضعیف             │
│ آنتروپی │ 37.6 بیت         │
└─────────┴──────────────────┘
```

### 🎲 `pdev random` — مقادیر تصادفی

```bash
$ pdev random int 1 100
42

$ pdev random str --length 16
aB3kL9mN2pQ8xY4z

$ pdev random choice a b c d
b

$ pdev random coin
شیر

$ pdev random dice --sides 20
17

$ pdev random nanoid
V1StGXR8_Z5jdHi6B-myT
```

### ✍️ `pdev text` — دستورات پیشرفتهٔ جدید

```bash
$ pdev text slug "سلام دنیا"
سلام-دنیا

$ pdev text slug "Hello, World! 2024" --max-length 15
hello-world-2024

$ pdev text case upper "hello world"
HELLO WORLD

$ pdev text case title "hello world"
Hello World

$ pdev text diff "line1\nline2" "line1\nline3"
- line2
+ line3

$ pdev text regex "\d+" "a1b22c333"
✓ مطابقت یافت شد.
تعداد: 3
  • 1
  • 22
  • 333
```

### 🔗 `pdev url` — کار با URL

```bash
$ pdev url encode "سلام دنیا"
%D8%B3%D9%84%D8%A7%D9%85%20%D8%AF%D9%86%DB%8C%D8%A7

$ pdev url decode "%D8%B3%D9%84%D8%A7%D9%85"
سلام

$ pdev url parse "https://example.com:8080/path?x=1&y=2#frag"
┏━━━━━━━━ 🔗 URL ━━━━━━━━┓
┃ بخش     │ مقدار        ┃
┡━━━━━━━━━╇━━━━━━━━━━━━━┩
│ scheme   │ https        │
│ netloc   │ example.com:8080 │
│ host     │ example.com  │
│ port     │ 8080         │
│ path     │ /path        │
│ query.x  │ 1            │
│ query.y  │ 2            │
│ fragment │ frag         │
└──────────┴──────────────┘

$ pdev url build name=ali age=30
name=ali&age=30
```

### ⏱  `pdev time` — timestamp و مدت زمان

```bash
$ pdev time now
1737000000

$ pdev time from-unix 0
1970-01-01 00:00:00 UTC

$ pdev time to-unix "2024-01-01 12:00:00"
1704110400

$ pdev time duration "2h30m"
┏━━━━━━━━ ⏱  مدت زمان ━━━━━━━━┓
┃ شاخص    │ مقدار            ┃
┡━━━━━━━━━╇━━━━━━━━━━━━━━━━━┩
│ ثانیه   │ 9,000            │
│ خوانا   │ 2 ساعت و 30 دقیقه│
└─────────┴──────────────────┘

$ pdev time ago 1700000000
14 روز و 3 ساعت پیش
```




###  `pdev date` — تبدیل و محاسبهٔ تاریخ

```bash
$ pdev date to-jalali 2024-03-21
1403/01/02

$ pdev date to-gregorian 1403/01/02
2024-03-21

$ pdev date now
┏━━━━━━━━━  اکنون ━━━━━━━━━┓
┃ تقویم  │ مقدار              ┃
┡━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━┩
│ میلادی │ 2026-09-11 14:32:01│
│ شمسی   │ 1405/06/20 14:32:01│
│ روز    │جمعه             │
└─────────┴────────────────────┘

$ pdev date diff 1402/01/01 1403/01/01
اختلاف: 365 روز
```

### 🎨 `pdev color` — کار با رنگ‌ها

```bash
$ pdev color convert "#ff0000"
┏━━━━━━━━━━━ 🎨 #ff0000 ━━━━━━━━━━┓
┃ فرمت    │ مقدار                  ┃
┡━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━┩
│ HEX      │ #ff0000               │
│ RGB      │ rgb(255, 0, 0)        │
│ HSL      │ hsl(0, 100%, 50%)     │
│ روشنایی  │ 50.0%                 │
│ نمایش    │ ██████████            │
└──────────┴───────────────────────┘

$ pdev color palette "#ff8800" --count 5
$ pdev color random --pleasant --count 3
$ pdev color contrast "#000" "#fff"
نسبت کنتراست: 21.00:1
سطح WCAG: AAA ✓
$ pdev color complement "#ff0000"
```

### 📱 `pdev qrcode` — تولید QR Code

```bash
$ pdev qrcode "سلام دنیا"
▄▄▄▄▄▄▄  ▄  ▄▄▄▄▄▄▄
█ ▄▄▄ █ █▄▀█ █ ▄▄▄ █
█ ███ █ ▄▀ ▀ █ ███ █
█▄▄▄▄▄█ ▀▄▀ █▄▄▄▄▄█
...

$ pdev qrcode "https://github.com" -o qr.png
✓ ذخیره شد: qr.png

$ pdev qrcode "متن فارسی" -e H --box-size 15 -o high.png
```

### 🖼  `pdev image` — اطلاعات و تبدیل تصویر

```bash
$ pdev image info photo.jpg
┏━━━━━━━━━━━ 🖼  photo.jpg ━━━━━━━━━━┓
┃ شاخص       │ مقدار                ┃
┡━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━┩
│ فرمت        │ JPEG                 │
│ حالت رنگی   │ RGB                  │
│ ابعاد       │ 1920 × 1080          │
│ اندازه      │ 245.3 KB             │
└─────────────┴──────────────────────┘

$ pdev image resize photo.jpg 800
✓ ذخیره شد: photo_resized.jpg

$ pdev image convert photo.png photo.jpg --quality 85
✓ ذخیره شد: photo.jpg
```

###  `pdev number` — تبدیل و قالب‌بندی اعداد


```bash
$ pdev number to-persian 1234567
۱۲۳۴۵۶۷

$ pdev number to-english ۱۲۳۴۵۶۷
1234567

$ pdev number format 1234567
1,234,567

$ pdev number words 1234
یک هزار و دویست و سی و چهار
```

###  `pdev text` — پاک‌سازی و پردازش متن

```bash
$ pdev text halfspace "می روم"
می‌روم

$ pdev text normalize "سلام  دنيا"
سلام دنیا

$ pdev text reverse "سلام"
مالس

$ pdev text stats "یک متن نمونه"
┏━━━━━━━━━━  آمار متن ━━━━━━━━━━┓
┃ شاخص              │ مقدار       ┃
┡━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━┩
│ کاراکترها         │          12 │
│ کاراکترهای غیرفاصله│         10 │
│ کلمات             │           3 │
│ خطوط              │           1 │
│ جملات             │           1 │
└───────────────────┴─────────────┘
```

پشتیبانی از stdin:

```bash
$ echo "می روم" | pdev text halfspace
می‌روم
```

### `pdev uuid` — تولید UUID

```bash
$ pdev uuid new
c4f9e78c-2b8a-4b8c-9d2f-3e8a1b5f6c7d

$ pdev uuid new --count 3
...

$ pdev uuid short
3q2_4rT9wZkA8bC1dE5fG7
```

###  `pdev json` — کار با JSON

```bash
$ pdev json pretty data.json
{
  "name": "علی",
  "age": 30
}

$ pdev json minify data.json
{"name":"علی","age":30}

$ pdev json validate data.json
✓ JSON معتبر است.

$ pdev json keys data.json
• name
• age

$ pdev json flatten nested.json
{
  "user.name": "ali",
  "user.tags[0]": "a",
  "user.tags[1]": "b"
}
```

---

##  گزینه‌های سراسری

| گزینه | توضیح |
|-------|-------|
| `--version`, `-V` | نمایش نسخه |
| `--verbose`, `-v` | خروجی با جزئیات بیشتر |
| `--quiet`, `-q` | کاهش پیام‌های اضافی |
| `--help` | راهنما |

---

## Completion

پس از نصب، برای فعال‌سازی auto-completion:

```bash
# bash
pdev --install-completion bash && source ~/.bashrc

# zsh
pdev --install-completion zsh && source ~/.zshrc

# PowerShell (Windows)
pdev --install-completion powershell
```

---

## توسعه

```bash
git clone https://github.com/your-username/persian-devkit
cd persian-devkit
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
pytest
```

ساختار پروژه:

```
persian-devkit/
├── src/
│ └── persian_devkit/
│ ├── init.py
│ ├── main.py
│ ├── cli.py
│ ├── commands/
│ │ ├── init.py
│ │ ├── date_cmd.py
│ │ ├── number_cmd.py
│ │ ├── text_cmd.py
│ │ ├── uuid_cmd.py
│ │ └── json_cmd.py
│ └── utils/
│ ├── init.py
│ ├── date_utils.py
│ ├── number_utils.py
│ └── text_utils.py
├── tests/
│ ├── test_date.py
│ ├── test_number.py
│ ├── test_text.py
│ ├── test_uuid.py
│ └── test_json.py
├── pyproject.toml
├── README.md
├── LICENSE
└── requirements.txt 
```

---

##  انتشار در PyPI

### آماده‌سازی

```bash
pip install --upgrade build twine
```

### بیلد

```bash
rm -rf dist/ build/ src/*.egg-info
python -m build
```

این دستور دو فایل در `dist/` می‌سازد:
- `persian_devkit-0.1.0-py3-none-any.whl`
- `persian_devkit-0.1.0.tar.gz`

### تست محلی

```bash
python -m twine check dist/*
pip install dist/*.whl
pdev --version
```

### آپلود به TestPyPI (پیشنهادی)

```bash
python -m twine upload --repository testpypi dist/*
pip install -i https://test.pypi.org/simple/ persian-devkit
```

### آپلود به PyPI

```bash
python -m twine upload dist/*
```

سپس هر کاربر می‌تواند با یک دستور نصب کند:

```bash
pip install persian-devkit
```

>  برای اطلاعات بیشتر دربارهٔ `~/.pypirc` و کلیدهای API، به [مستندات رسمی PyPI](https://packaging.python.org/) مراجعه کن.

---

##  مجوز

MIT © 2026 — برای جزئیات `LICENSE` را ببین.

### نکتهٔ کاربران ویندوز

برای پشتیبانی کامل از متن فارسی در CMD، ابتدا در ترمینال خود این را اجرا کنید:

    chcp 65001

یا از PowerShell استفاده کنید که به‌طور پیش‌فرض UTF-8 است:

    "می روم" | pdev text halfspace












###  `pdev yaml` / `pdev toml` / `pdev csv` / `pdev env`

تبدیل و اعتبارسنجی داده‌های ساختاریافته:

```bash
$ pdev yaml to-json config.yaml
$ pdev yaml from-json data.json -o config.yaml
$ pdev toml to-json pyproject.toml
$ pdev csv show data.csv
$ pdev csv to-json data.csv
$ pdev csv filter data.csv age "^3" --ignore-case
$ pdev env show .env           # مقادیر حساس مخفی
$ pdev env to-shell .env       # export KEY=...
$ pdev env sort .env -o .env.sorted
```






### 🔍 `pdev jq` — کوئری JSON (جایگزین سادهٔ jq)

```bash
$ echo '{"user": {"name": "علی", "age": 30}}' | pdev jq .user.name -r
علی

$ pdev jq .items[0] -f data.json
$ pdev jq '.items[*].name' -f data.json -r
$ pdev jq '.config.database.host' -f config.json -r
$ pdev jq '["key with space"]' -f d.json
```

مسیرهای پشتیبانی‌شده:
- `.key` → دسترسی به کلید
- `.a.b.c` → تودرتو
- `.items[0]` → اندیس آرایه
- `.items[*]` → همهٔ عناصر
- `["key with space"]` → کلید با کاراکتر خاص

###  `pdev lorem` — متن نمونهٔ فارسی

```bash
$ pdev lorem sentence
زبان فارسی گنجینه‌ای از ادبیات و فرهنگ است.

$ pdev lorem paragraph -s 3
...
$ pdev lorem words -c 6
$ pdev lorem all -p 3 -s 4
```

###  `pdev name` — نام و دادهٔ نمونهٔ فارسی

```bash
$ pdev name full
علی احمدی

$ pdev name full -g female -c 3
سارا رضایی
مریم حسینی
فاطمه محمدی

$ pdev name email
ali.ahmadi42@example.com

$ pdev name profile -c 3 -j
[
  {"name": "علی احمدی", "email": "...", "city": "تهران"},
  ...
]
```





###  `pdev license` — تولید لایسنس

```bash
$ pdev license list
$ pdev license show MIT -a "علی رضایی" -y 2024
$ pdev license new Apache-2.0 -a "Sara" -o LICENSE
```

###  `pdev gitignore` — تولید .gitignore

```bash
$ pdev gitignore list
$ pdev gitignore show python
$ pdev gitignore new python node macos -o .gitignore
$ pdev gitignore new rust --append
```

###   `pdev scaffold` — ساخت پروژه از قالب

```bash
$ pdev scaffold python myproject
✓ پروژه ساخته شد: /home/user/myproject
  • README.md
  • pyproject.toml
  • src/myproject/main.py
  • tests/test_main.py

$ pdev scaffold node myapp --target ./projects
$ pdev scaffold minimal hello
```

###  `pdev template` — رندر قالب متنی

```bash
$ echo "سلام {{name}} از {{city}}" > greet.txt
$ pdev template greet.txt -D name=علی -D city=تهران
سلام علی از تهران

$ pdev template vars greet.txt
متغیرهای یافت‌شده (2):
  • name
  • city

$ pdev template config.tpl -D port=8080 -o config.yaml
```

