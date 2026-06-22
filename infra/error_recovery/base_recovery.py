# نظام استرداد الأخطاء الأساسي — يُستخدم من كل طبقات المشروع
import time
import logging
from pathlib import Path

# إعداد الـ logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s — %(levelname)s — %(message)s"
)
logger = logging.getLogger(__name__)


def retry(func, attempts: int = 2, delay: float = 1.0):
    """يحاول تشغيل الدالة عدد مرات محدد — عند الفشل ينتظر ثم يعيد"""
    last_error = None
    for attempt in range(attempts):
        try:
            return func()
        except Exception as e:
            last_error = e
            logger.warning(f"محاولة {attempt + 1}/{attempts} فشلت: {e}")
            if attempt < attempts - 1:
                time.sleep(delay)
    logger.error(f"فشل نهائي بعد {attempts} محاولات: {last_error}")
    raise last_error


class RecoveryResult:
    """نتيجة عملية الاسترداد"""
    def __init__(self, success: bool, data=None, error: str = "", used_fallback: bool = False):
        self.success = success          # هل نجحت العملية؟
        self.data = data                # البيانات الناتجة
        self.error = error              # رسالة الخطأ إن وجدت
        self.used_fallback = used_fallback  # هل استُخدم الـ fallback؟

    def __repr__(self):
        return f"RecoveryResult(success={self.success}, used_fallback={self.used_fallback})"
