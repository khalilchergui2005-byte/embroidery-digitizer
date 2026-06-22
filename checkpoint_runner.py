"""
checkpoint_runner.py — يتحقق من البيئة بأمر واحد
شغّله بعد الذرة 00 وبعد كل مرحلة رئيسية
"""
import sys

results = []

# تحقق 1: Python 3.11+
ok = sys.version_info >= (3, 11)
results.append(("Python 3.11+", ok,
    f"الإصدار الحالي: {sys.version.split()[0]}" if ok
    else f"إصدارك {sys.version.split()[0]} — ثبّت Python 3.11"))

# تحقق 2: المكتبات الأساسية
libs = [
    ("pyembroidery", "pyembroidery"),
    ("rembg", "rembg"),
    ("PIL (Pillow)", "PIL"),
    ("cv2 (OpenCV)", "cv2"),
    ("numpy", "numpy"),
    ("scipy", "scipy"),
    ("sklearn (scikit-learn)", "sklearn"),
    ("networkx", "networkx"),
    ("pydantic", "pydantic"),
    ("imagehash", "imagehash"),
    ("svglib", "svglib"),
]
for name, module in libs:
    try:
        __import__(module)
        results.append((f"مكتبة {name}", True, ""))
    except ImportError:
        results.append((f"مكتبة {name}", False,
            f"ثبّتها: pip install {module}"))

# تحقق 3: python-telegram-bot
try:
    import telegram
    v = telegram.__version__
    ok = int(v.split(".")[0]) >= 22
    results.append(("python-telegram-bot v22+", ok,
        f"الإصدار: {v}" if ok else f"إصدارك {v} قديم — pip install python-telegram-bot==22.8"))
except ImportError:
    results.append(("python-telegram-bot", False, "pip install python-telegram-bot==22.8"))

# تحقق 4: pillow-heif
try:
    import pillow_heif
    results.append(("pillow-heif", True, ""))
except ImportError:
    results.append(("pillow-heif", False, "pip install pillow-heif>=1.4.0"))

# تحقق 5: ملف .env
from pathlib import Path
env_exists = Path(".env").exists()
results.append((".env موجود", env_exists,
    "اصنع ملف .env في جذر المشروع" if not env_exists else ""))

# تحقق 6: GEMINI_API_KEY في .env
if env_exists:
    content = Path(".env").read_text()
    has_key = "GEMINI_API_KEY" in content and "your_key_here" not in content
    results.append(("GEMINI_API_KEY", has_key,
        "أضف GEMINI_API_KEY=مفتاحك في ملف .env" if not has_key else ""))

# تحقق 7: مجلد samples/
samples_ok = (Path("samples") / "test_simple.jpg").exists()
results.append(("samples/ جاهزة", samples_ok,
    "أضف صور اختبار في مجلد samples/" if not samples_ok else ""))

# طباعة النتائج
print("\n" + "="*50)
print("  تقرير فحص البيئة — checkpoint_runner.py")
print("="*50)
all_ok = True
for name, ok, msg in results:
    status = "✅" if ok else "❌"
    line = f"  {status}  {name}"
    if msg:
        line += f"\n       → {msg}"
    print(line)
    if not ok:
        all_ok = False

print("="*50)
if all_ok:
    print("  ✅ كل شيء جاهز — يمكنك البدء بالذرة 01")
else:
    print("  ❌ أصلح الأخطاء أعلاه ثم شغّل الملف من جديد")
print("="*50 + "\n")