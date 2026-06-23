import os
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent
OUTPUTS_DIR = BASE_DIR / "outputs"
SAMPLES_DIR = BASE_DIR / "samples"
DATA_DIR = BASE_DIR / "data"

def validate_env() -> None:
    required = {
        "GEMINI_API_KEY": os.getenv("GEMINI_API_KEY", ""),
        "TELEGRAM_BOT_TOKEN": os.getenv("TELEGRAM_BOT_TOKEN", ""),
    }
    missing = [k for k, v in required.items() if not v]
    if missing:
        raise EnvironmentError(f"مفاتيح ناقصة في .env: {', '.join(missing)}")
