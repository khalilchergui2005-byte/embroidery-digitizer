import logging
from dotenv import load_dotenv
load_dotenv()
from config.settings import validate_env
from bot.telegram_bot import run_bot

logging.basicConfig(format="%(asctime)s - %(levelname)s - %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)

def main() -> None:
    try:
        validate_env()
        logger.info("البيئة جاهزة")
    except EnvironmentError as e:
        logger.error(f"خطأ في البيئة: {e}")
        return
    logger.info("تشغيل البوت...")
    run_bot()

if __name__ == "__main__":
    main()
