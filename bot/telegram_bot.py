# بوت Telegram — نقطة الدخول الرئيسية للزبائن
import os
import logging
from pathlib import Path
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# تحميل متغيرات البيئة
load_dotenv()
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")

# Cloudflare Worker — يتجاوز الحجب من الجزائر
# المكتبة ستضيف /{token}/{method} تلقائياً بعد هذا الـ URL
PROXY_BASE_URL = os.getenv(
    "TELEGRAM_PROXY_URL",
    "https://telegram-proxy.khalilchergui2005.workers.dev"
)

# إعداد الـ logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """رسالة الترحيب عند /start"""
    await update.message.reply_text(
        "مرحباً! 🧵\n"
        "أرسل صورة التصميم وسأحوّلها لملف رشمة جاهز للمكينة.\n\n"
        "الصيغ المقبولة: JPG, PNG, WEBP, HEIC\n"
        "الحجم الأقصى: 10MB",
        do_quote=True
    )


async def handle_image(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """يستقبل الصورة من الزبون"""
    await update.message.reply_text(
        "✅ استلمت صورتك — جارٍ المعالجة...\n"
        "سيصلك الملف خلال دقيقة.",
        do_quote=True
    )
    logger.info(f"صورة مستلمة من: {update.effective_user.id}")


async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """يرد على الرسائل النصية"""
    await update.message.reply_text(
        "أرسل صورة التصميم للبدء. 📸",
        do_quote=True
    )


def run_bot() -> None:
    """تشغيل البوت عبر Cloudflare Proxy"""
    if not TELEGRAM_BOT_TOKEN:
        raise EnvironmentError("TELEGRAM_BOT_TOKEN غير موجود في .env")

    # base_url بدون توكن — المكتبة تضيفه تلقائياً
    base_url = f"{PROXY_BASE_URL}/"

    logger.info(f"Proxy base_url: {base_url}")

    app = (
        Application.builder()
        .token(TELEGRAM_BOT_TOKEN)
        .base_url(base_url)
        .build()
    )

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.PHOTO | filters.Document.IMAGE, handle_image))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))

    logger.info("البوت يعمل...")
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    run_bot()
