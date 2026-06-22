# fallbacks الغرزات — عند فشل حساب الغرزات يرجع لقيم آمنة
from pathlib import Path
from config.constants import (
    DST_MAX_STITCH_MM, SATIN_OPTIMAL_MM,
    FILL_OPTIMAL_MM, RUNNING_OPTIMAL_MM,
    UNDERLAY_MM, DENSITY_MEDIUM_FABRIC
)
from infra.error_recovery.base_recovery import RecoveryResult


def safe_stitch_length(length_mm: float) -> float:
    """يُعيد طول غرزة آمن — يرفض أي قيمة تتجاوز الحد الفيزيائي"""
    if length_mm > DST_MAX_STITCH_MM:
        return DST_MAX_STITCH_MM  # حماية المكينة أولاً
    if length_mm < 0.1:
        return 0.1
    return length_mm


def fallback_stitch_params(stitch_type: str = "Fill") -> dict:
    """قيم افتراضية آمنة لكل نوع غرزة عند فشل الحساب"""
    defaults = {
        "Satin": {
            "length_mm": SATIN_OPTIMAL_MM,
            "density": DENSITY_MEDIUM_FABRIC,
            "underlay": UNDERLAY_MM,
            "angle": 45
        },
        "Fill": {
            "length_mm": FILL_OPTIMAL_MM,
            "density": DENSITY_MEDIUM_FABRIC,
            "underlay": UNDERLAY_MM,
            "angle": 45
        },
        "Running": {
            "length_mm": RUNNING_OPTIMAL_MM,
            "density": DENSITY_MEDIUM_FABRIC,
            "underlay": 0,
            "angle": 0
        },
    }
    return defaults.get(stitch_type, defaults["Fill"])


def validate_stitch_list(stitches: list) -> RecoveryResult:
    """يتحقق من كل الغرزات — يرفض الملف إن وجد خطر فيزيائي"""
    violations = []
    for i, stitch in enumerate(stitches):
        length = stitch.get("length_mm", 0)
        if length > DST_MAX_STITCH_MM:
            violations.append(f"غرزة {i}: {length}mm تتجاوز {DST_MAX_STITCH_MM}mm")

    if violations:
        return RecoveryResult(
            success=False,
            error=f"خطر فيزيائي: {len(violations)} غرزة خطيرة — {violations[0]}"
        )
    return RecoveryResult(success=True, data=stitches)
