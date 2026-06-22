# fallbacks الذكاء الاصطناعي — عند فشل Gemini يرجع لقواعد محلية
from pathlib import Path
from infra.error_recovery.base_recovery import RecoveryResult


def local_fallback_rules(image_bytes: bytes = None) -> dict:
    """قواعد محلية ثابتة عند فشل Gemini كلياً — لا إنترنت مطلوب"""
    return {
        "regions": [
            {
                "id": "region_1",
                "description": "منطقة افتراضية",
                "stitch_type": "Fill",
                "color_approx": "#000000",
                "too_thin": False,
                "order": 1
            }
        ],
        "has_arabic_text": False,
        "has_gradients": False,
        "complexity": "ASSISTED",
        "reject_reason": None,
        "embroidery_order": ["region_1"],
        "used_fallback": True
    }


def parse_gemini_response(text: str) -> dict:
    """يحوّل رد Gemini النصي لـ dict — مع تنظيف JSON التالف"""
    import json
    import re

    # إزالة backticks وكلمة json
    clean = re.sub(r"`json|`", "", text).strip()

    try:
        return json.loads(clean)
    except json.JSONDecodeError:
        # محاولة استخراج أول JSON صالح في النص
        match = re.search(r"\{.*\}", clean, re.DOTALL)
        if match:
            try:
                return json.loads(match.group())
            except json.JSONDecodeError:
                pass
    # فشل كل المحاولات → قواعد محلية
    return local_fallback_rules()


def gemini_timeout_fallback() -> RecoveryResult:
    """عند انتهاء وقت Gemini"""
    return RecoveryResult(
        success=True,
        data=local_fallback_rules(),
        error="Gemini timeout — استُخدمت القواعد المحلية",
        used_fallback=True
    )
