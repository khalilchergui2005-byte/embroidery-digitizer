# فصل الخلفية — ثلاثة مستويات تلقائية
from rembg import remove, new_session
from infra.error_recovery.image_fallbacks import grabcut_fallback
from infra.error_recovery.base_recovery import RecoveryResult
from config.constants import EDGE_COUNT_THRESHOLD

# تحميل النماذج مرة واحدة عند الاستيراد
session_simple = new_session("u2net")
session_complex = new_session("birefnet-general")


def separate_background(image_bytes: bytes, edge_count: int = 0) -> RecoveryResult:
    """
    يفصل الخلفية تلقائياً حسب تعقيد الصورة
    المستوى 1: u2net — سريع، 90% من الحالات
    المستوى 2: birefnet-general — للخلفيات المعقدة
    المستوى 3: GrabCut — fallback كامل، لا إنترنت
    """
    # المستوى 1: صورة بسيطة
    if edge_count < EDGE_COUNT_THRESHOLD:
        try:
            result = remove(image_bytes, session=session_simple)
            return RecoveryResult(success=True, data=result, used_fallback=False)
        except Exception as e:
            pass

    # المستوى 2: خلفية معقدة
    try:
        result = remove(image_bytes, session=session_complex)
        return RecoveryResult(success=True, data=result, used_fallback=False)
    except Exception as e:
        pass

    # المستوى 3: GrabCut — لا يفشل أبداً
    try:
        result = grabcut_fallback(image_bytes)
        return RecoveryResult(
            success=True,
            data=result,
            error="استُخدم GrabCut كـ fallback",
            used_fallback=True
        )
    except Exception as e:
        return RecoveryResult(success=False, error=f"فشل فصل الخلفية كلياً: {e}")
