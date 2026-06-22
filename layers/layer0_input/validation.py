# التحقق من جودة الصورة — يرفض الصور الضعيفة قبل المعالجة
import cv2
import numpy as np
from pathlib import Path
from config.constants import (
    REJECTION_BLUR_MIN, REJECTION_MIN_DIMENSION,
    QUALITY_MIN_DIMENSION_PX, QUALITY_BLUR_LAPLACIAN
)
from infra.error_recovery.base_recovery import RecoveryResult


def measure_blur(image_bytes: bytes) -> float:
    """يقيس مستوى الضبابية — Laplacian variance — أقل = أضبط"""
    nparr = np.frombuffer(image_bytes, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_GRAYSCALE)
    if img is None:
        return 0.0
    return float(cv2.Laplacian(img, cv2.CV_64F).var())


def validate_image(image_bytes: bytes, filename: str = "image.jpg") -> RecoveryResult:
    """
    يتحقق من صلاحية الصورة للمعالجة
    يرفض: صغيرة جداً، ضبابية جداً، تالفة
    """
    nparr = np.frombuffer(image_bytes, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

    if img is None:
        return RecoveryResult(success=False, error="لا يمكن قراءة الصورة — ملف تالف")

    h, w = img.shape[:2]

    # رفض: أبعاد صغيرة جداً
    if w < REJECTION_MIN_DIMENSION or h < REJECTION_MIN_DIMENSION:
        return RecoveryResult(
            success=False,
            error=f"الصورة صغيرة جداً: {w}×{h}px — الحد الأدنى {REJECTION_MIN_DIMENSION}px"
        )

    # قياس الضبابية
    blur_score = measure_blur(image_bytes)

    # رفض: ضبابية جداً
    if blur_score < REJECTION_BLUR_MIN:
        return RecoveryResult(
            success=False,
            error=f"الصورة ضبابية جداً (score={blur_score:.1f}) — أرسل صورة أوضح"
        )

    # تحديد جودة الصورة
    needs_upscale = w < QUALITY_MIN_DIMENSION_PX or h < QUALITY_MIN_DIMENSION_PX
    needs_sharpen = blur_score < QUALITY_BLUR_LAPLACIAN

    return RecoveryResult(
        success=True,
        data={
            "width": w,
            "height": h,
            "blur_score": blur_score,
            "needs_upscale": needs_upscale,
            "needs_sharpen": needs_sharpen,
            "quality": "high" if not needs_upscale and not needs_sharpen else "medium"
        }
    )


def count_edges(image_bytes: bytes) -> int:
    """يعد حواف الصورة — يحدد مستوى التعقيد للـ background separation"""
    nparr = np.frombuffer(image_bytes, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_GRAYSCALE)
    if img is None:
        return 0
    edges = cv2.Canny(img, 100, 200)
    return int(np.sum(edges > 0))
