# استقبال الصور — أول نقطة دخول في الـ pipeline
import io
from pathlib import Path
from PIL import Image
from pillow_heif import register_heif_opener
from config.constants import MAX_FILE_SIZE_BYTES
from infra.error_recovery.base_recovery import RecoveryResult

# تفعيل دعم صور HEIC من iOS
register_heif_opener()

# الصيغ المقبولة
ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".heic", ".heif", ".bmp"}
ALLOWED_MIME_TYPES = {
    "image/jpeg", "image/png", "image/webp",
    "image/heic", "image/heif", "image/bmp"
}


def ingest_image(image_bytes: bytes, filename: str = "image.jpg") -> RecoveryResult:
    """
    يستقبل الصورة ويتحقق منها — أول خطوة في الـ pipeline
    المدخل: bytes الصورة + اسم الملف
    المخرج: RecoveryResult يحتوي dict بمعلومات الصورة
    """
    # التحقق من الحجم
    size_bytes = len(image_bytes)
    if size_bytes > MAX_FILE_SIZE_BYTES:
        return RecoveryResult(
            success=False,
            error=f"الملف كبير جداً: {size_bytes / 1024 / 1024:.1f}MB — الحد الأقصى 10MB"
        )

    if size_bytes == 0:
        return RecoveryResult(success=False, error="الملف فارغ")

    # التحقق من الصيغة
    ext = Path(filename).suffix.lower()
    if ext not in ALLOWED_EXTENSIONS:
        return RecoveryResult(
            success=False,
            error=f"صيغة غير مدعومة: {ext} — المقبول: {', '.join(ALLOWED_EXTENSIONS)}"
        )

    # محاولة فتح الصورة
    try:
        img = Image.open(io.BytesIO(image_bytes))
        img.verify()  # تحقق من سلامة الملف
        img = Image.open(io.BytesIO(image_bytes))  # إعادة الفتح بعد verify
        width, height = img.size
        mode = img.mode
    except Exception as e:
        return RecoveryResult(success=False, error=f"ملف تالف أو غير صالح: {e}")

    return RecoveryResult(
        success=True,
        data={
            "bytes": image_bytes,
            "filename": filename,
            "width": width,
            "height": height,
            "mode": mode,
            "size_bytes": size_bytes,
            "extension": ext,
        }
    )


def bytes_to_pil(image_bytes: bytes) -> Image.Image:
    """تحويل bytes لصورة PIL — للاستخدام الداخلي"""
    return Image.open(io.BytesIO(image_bytes))
