# راهنمای مشارکت در persian-devkit

ممنون که می‌خواهی کمک کنی! 🙏

## 🎯 راه‌های مشارکت

- 🐛 **گزارش باگ** — در [Issues](https://github.com/sobhanosmanzadeh1-beep/persian-devkit/issues) یک issue باز کن
- 💡 **پیشنهاد قابلیت** — از قالب Feature Request استفاده کن
- 📝 **بهبود مستندات** — README، docstring‌ها، ترجمه
- 🔧 **ارسال Pull Request** — کد، تست، یا هر دو
- 🌍 **ترجمه** — کمک به ترجمهٔ پیام‌ها و مستندات

## 🚀 راه‌اندازی محیط توسعه

```bash
# ۱. کلون پروژه
git clone https://github.com/sobhanosmanzadeh1-beep/persian-devkit.git
cd persian-devkit

# ۲. محیط مجازی
python -m venv .venv
source .venv/bin/activate  # ویندوز: .venv\Scripts\activate

# ۳. نصب editable با وابستگی‌های dev
pip install -e ".[dev]"

# ۴. اجرای تست‌ها
pytest

# ۵. اجرای CLI در حالت توسعه
pdev --help
