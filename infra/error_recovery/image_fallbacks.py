# fallbacks معالجة الصور — عند فشل rembg أو أي مكتبة صور
import cv2
import numpy as np
from pathlib import Path
from infra.error_recovery.base_recovery import RecoveryResult


def grabcut_fallback(image_bytes: bytes) -> bytes:
    """فصل الخلفية بـ GrabCut — لا نموذج، لا إنترنت، دائماً يعمل"""
    # تحويل bytes لمصفوفة numpy
    nparr = np.frombuffer(image_bytes, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

    # إنشاء mask وتطبيق GrabCut
    mask = np.zeros(img.shape[:2], np.uint8)
    bgd_model = np.zeros((1, 65), np.float64)
    fgd_model = np.zeros((1, 65), np.float64)

    # مستطيل وسط الصورة كمنطقة الموضوع
    h, w = img.shape[:2]
    rect = (int(w * 0.05), int(h * 0.05), int(w * 0.9), int(h * 0.9))

    cv2.grabCut(img, mask, rect, bgd_model, fgd_model, 5, cv2.GC_INIT_WITH_RECT)

    # استخراج الموضوع
    mask2 = np.where((mask == 2) | (mask == 0), 0, 1).astype("uint8")
    result = img * mask2[:, :, np.newaxis]

    # إضافة قناة alpha
    b, g, r = cv2.split(result)
    alpha = mask2 * 255
    rgba = cv2.merge([b, g, r, alpha])

    # تحويل لـ bytes
    _, buffer = cv2.imencode(".png", rgba)
    return buffer.tobytes()


def resize_safe(image_bytes: bytes, max_dim: int = 2000) -> bytes:
    """تصغير الصورة بأمان إن كانت كبيرة جداً"""
    nparr = np.frombuffer(image_bytes, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

    h, w = img.shape[:2]
    if max(h, w) <= max_dim:
        return image_bytes  # لا تغيير مطلوب

    # حساب النسبة
    scale = max_dim / max(h, w)
    new_w = int(w * scale)
    new_h = int(h * scale)

    resized = cv2.resize(img, (new_w, new_h), interpolation=cv2.INTER_LANCZOS4)
    _, buffer = cv2.imencode(".jpg", resized, [cv2.IMWRITE_JPEG_QUALITY, 95])
    return buffer.tobytes()


def to_png_safe(image_bytes: bytes) -> RecoveryResult:
    """تحويل أي صورة لـ PNG بأمان"""
    try:
        nparr = np.frombuffer(image_bytes, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_UNCHANGED)
        if img is None:
            return RecoveryResult(success=False, error="لا يمكن قراءة الصورة")
        _, buffer = cv2.imencode(".png", img)
        return RecoveryResult(success=True, data=buffer.tobytes())
    except Exception as e:
        return RecoveryResult(success=False, error=str(e))
