"""تولید داده‌های نمونهٔ فارسی (Lorem، نام، شهر)."""
from __future__ import annotations

import secrets

# متن لورم فارسی — جملات معنادار برای پر کردن قالب‌ها
_LOREM_SENTENCES = [
    "در این روزگار، فناوری به سرعت در حال تغییر است.",
    "برنامه‌نویسی هنری است که نیازمند صبر و دقت است.",
    "هر مسئله‌ای راه‌حلی دارد، فقط باید آن را پیدا کرد.",
    "کتاب‌ها بهترین دوستان انسان در تنهایی هستند.",
    "زبان فارسی گنجینه‌ای از ادبیات و فرهنگ است.",
    "کار تیمی باعث می‌شود کارهای بزرگ به ثمر بنشینند.",
    "یادگیری مداوم کلید موفقیت در هر حرفه‌ای است.",
    "طراحی خوب نامرئی است؛ کاربر فقط راحتی را حس می‌کند.",
    "داده‌ها اگر درست تحلیل شوند، به دانش تبدیل می‌شوند.",
    "خلاقیت وقتی شکوفا می‌شود که ذهن آزاد باشد.",
    "کیفیت مهم‌تر از کمیت است در هر کاری.",
    "احترام به دیگران، اولین قدم در ساختن جامعه‌ای بهتر است.",
    "سادگی بالاترین درجهٔ پیچیدگی است.",
    "آینده از آن کسانی است که امروز یاد می‌گیرند.",
    "همکاری بین‌المللی می‌تواند بسیاری از مشکلات را حل کند.",
]

_FIRST_NAMES_MALE = [
    "علی", "محمد", "حسن", "حسین", "رضا", "امیر", "مهدی", "سعید", "احمد", "کاوه",
    "بهرام", "داریوش", "کوروش", "سیاوش", "آرش", "فریدون", "نوید", "پیمان", "بابک",
    "شاهین", "کیوان", "اردشیر", "پیروز", "فرهاد", "ساسان", "یاسر", "مانی",
]

_FIRST_NAMES_FEMALE = [
    "فاطمه", "زهرا", "مریم", "سارا", "نرگس", "الهام", "نازنین", "شیما", "پریسا", "نازلی",
    "نیلوفر", "شیرین", "لیلا", "ملیکا", "آیدا", "بهاره", "گلنار", "رعنا", "کتایون",
    "رودابه", "تهمینه", "فرنگیس", "یاسمن", "آزاده", "سیمین", "پروین", "مینا", "هستی",
]

_LAST_NAMES = [
    "احمدی", "محمدی", "رضایی", "حسینی", "موسوی", "کریمی", "صادقی", "جعفری", "قاسمی",
    "حیدری", "نجفی", "محمودی", "اکبری", "قربانی", "رحیمی", "شریفی", "نوری", "کاظمی",
    "زمانی", "مهدوی", "مرادی", "پورمحمدی", "سلطانی", "فرهادی", "امینی", "رستمی",
    "بهرامی", "صالحی", "طاهری", "یزدانی", "جهانگیری", "خسروی", "زندی", "سپهری",
]

_CITIES = [
    "تهران", "مشهد", "اصفهان", "کرج", "شیراز", "تبریز", "قم", "اهواز", "کرمانشاه",
    "ارومیه", "رشت", "زاهدان", "همدان", "کرمان", "یزد", "اردبیل", "بندرعباس",
    "اراک", "قزوین", "زنجان", "سنندج", "گرگان", "ساری", "بوشهر", "بیرجند",
    "خرم‌آباد", "ایلام", "سمنان", "یاسوج", "شهرکرد",
]

_DOMAINS = ["example.com", "test.ir", "demo.ir", "sample.org", "fake.net"]


#lorem


def random_sentence() -> str:
    """یک جملهٔ تصادفی فارسی."""
    return secrets.choice(_LOREM_SENTENCES)


def random_paragraph(sentences: int = 4) -> str:
    """پاراگراف با تعداد جملهٔ مشخص."""
    if sentences < 1:
        sentences = 1
    chosen = [secrets.choice(_LOREM_SENTENCES) for _ in range(sentences)]
    return " ".join(chosen)


def lorem_ipsum(paragraphs: int = 1, sentences_per_paragraph: int = 4) -> str:
    """متن لورم فارسی با تعداد پاراگراف مشخص."""
    if paragraphs < 1:
        paragraphs = 1
    return "\n\n".join(
        random_paragraph(sentences_per_paragraph) for _ in range(paragraphs)
    )


def random_words(count: int = 5) -> str:
    """چند کلمهٔ تصادفی از متن لورم."""
    all_words: list[str] = []
    for sent in _LOREM_SENTENCES:
        all_words.extend(sent.split())
    if count < 1:
        count = 1
    return " ".join(secrets.choice(all_words) for _ in range(count))


#name


def random_first_name(gender: str = "any") -> str:
    """نام کوچک تصادفی فارسی. gender: any|male|female"""
    if gender == "male":
        return secrets.choice(_FIRST_NAMES_MALE)
    if gender == "female":
        return secrets.choice(_FIRST_NAMES_FEMALE)
    return secrets.choice(_FIRST_NAMES_MALE + _FIRST_NAMES_FEMALE)


def random_last_name() -> str:
    """نام خانوادگی تصادفی فارسی."""
    return secrets.choice(_LAST_NAMES)


def random_full_name(gender: str = "any") -> str:
    """نام و نام خانوادگی فارسی."""
    return f"{random_first_name(gender)} {random_last_name()}"


def random_city() -> str:
    """نام شهر ایرانی."""
    return secrets.choice(_CITIES)


def random_email(first: str | None = None, last: str | None = None) -> str:
    """ایمیل تصادفی (بر پایهٔ نام)."""
    if first is None:
        first = random_first_name()
    if last is None:
        last = random_last_name()

    # تبدیل به ASCII برای سازگاری با ایمیل
    first_ascii = _transliterate(first)
    last_ascii = _transliterate(last)
    num = secrets.randbelow(1000)
    domain = secrets.choice(_DOMAINS)
    return f"{first_ascii}.{last_ascii}{num}@{domain}".lower()


_TRANSLIT_MAP = {
    "ع": "a", "ا": "a", "ب": "b", "پ": "p", "ت": "t", "ث": "s", "ج": "j",
    "چ": "ch", "ح": "h", "خ": "kh", "د": "d", "ذ": "z", "ر": "r", "ز": "z",
    "ژ": "zh", "س": "s", "ش": "sh", "ص": "s", "ض": "z", "ط": "t", "ظ": "z",
    "غ": "gh", "ف": "f", "ق": "gh", "ک": "k", "ك": "k", "گ": "g", "ل": "l",
    "م": "m", "ن": "n", "و": "v", "ه": "h", "ی": "y", "ي": "y", "ء": "",
    "آ": "a", "أ": "a", "إ": "e", "ؤ": "o", "ئ": "y", "\u200c": "",
    " ": "",
}


def _transliterate(text: str) -> str:
    """تبدیل سادهٔ حروف فارسی به لاتین (برای ایمیل و slug)."""
    return "".join(_TRANSLIT_MAP.get(c, c) for c in text)