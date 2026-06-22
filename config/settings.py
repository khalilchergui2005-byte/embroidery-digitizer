# إعدادات البيئة — تُقرأ من ملف .env
import os
from pathlib import Path

# مسار المشروع
BASE_DIR = Path(__file__).parent.parent

# مسارات المجلدات
OUTPUTS_DIR = BASE_DIR / "outputs"
SAMPLES_DIR = BASE_DIR / "samples"
DATA_DIR = BASE_DIR / "data"

# مفاتيح API — تُقرأ من .env فقط
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
SUPABASE_URL = os.getenv("SUPABASE_URL", "")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "")
ADMIN_TELEGRAM_ID = os.getenv("ADMIN_TELEGRAM_ID", "")

# التحقق من المفاتيح الإلزامية عند الاستيراد
def validate_env() -> None:
    required = {
        "GEMINI_API_KEY": GEMINI_API_KEY,
        "TELEGRAM_BOT_TOKEN": TELEGRAM_BOT_TOKEN,
    }
    missing = [k for k, v in required.items() if not v]
    if missing:
        raise EnvironmentError(
            f"مفاتيح ناقصة في .env: {', '.join(missing)}"
        )
