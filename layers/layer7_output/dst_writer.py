# كتابة ملف الرشمة — الذرة الأهم في المشروع
# validate_stitches_safe() إلزامي قبل أي كتابة
import pyembroidery
from pathlib import Path
from config.constants import DST_MAX_STITCH_MM, DST_MIN_STITCH_MM, MAX_STITCHES_SAFE
from infra.error_recovery.base_recovery import RecoveryResult
from infra.error_recovery.output_fallbacks import safe_write_file, ensure_output_dir


def validate_stitches_safe(stitch_list: list) -> None:
    """
    يرفض أي ملف فيه غرزة تتجاوز الحد الآمن — يحمي المكينة فيزيائياً
    استدعاء إلزامي قبل كل كتابة ملف — لا استثناء
    """
    if len(stitch_list) > MAX_STITCHES_SAFE:
        raise ValueError(
            f"عدد الغرزات {len(stitch_list)} يتجاوز الحد الآمن {MAX_STITCHES_SAFE}"
        )
    for i, stitch in enumerate(stitch_list):
        length = stitch.get("length_mm", 0)
        if length > DST_MAX_STITCH_MM:
            raise ValueError(
                f"خطأ أمان: الغرزة {i} طولها {length}mm تتجاوز {DST_MAX_STITCH_MM}mm — الملف لن يُكتب"
            )
        if length < 0:
            raise ValueError(f"خطأ: الغرزة {i} طولها سالب: {length}mm")


def write_dst(stitch_list: list, output_path: Path, metadata: dict = None) -> RecoveryResult:
    """
    يكتب ملف DST من قائمة الغرزات
    المدخل: قائمة غرزات + مسار الإخراج
    المخرج: RecoveryResult يحتوي مسار الملف
    """
    # 1. التحقق الأمني أولاً — إلزامي
    try:
        validate_stitches_safe(stitch_list)
    except ValueError as e:
        return RecoveryResult(success=False, error=str(e))

    # 2. إنشاء كائن التطريز
    pattern = pyembroidery.EmbPattern()

    # 3. إضافة metadata
    if metadata:
        pattern.metadata("name", metadata.get("name", "رشمة"))
        pattern.metadata("author", metadata.get("author", "embroidery-digitizer"))

    # 4. إضافة الغرزات
    current_color = None
    for stitch in stitch_list:
        color = stitch.get("color", (0, 0, 0))
        x = stitch.get("x", 0)
        y = stitch.get("y", 0)
        stitch_type = stitch.get("type", "stitch")

        # تغيير اللون عند الحاجة
        if color != current_color:
            if current_color is not None:
                pattern.add_command(pyembroidery.COLOR_CHANGE)
            r, g, b = color
            pattern.add_thread({"color": r << 16 | g << 8 | b, "name": f"thread_{r}_{g}_{b}"})
            current_color = color

        # إضافة الغرزة
        if stitch_type == "jump":
            pattern.add_command(pyembroidery.JUMP, x, y)
        else:
            pattern.add_stitch_absolute(pyembroidery.STITCH, x, y)

    # 5. إنهاء الملف
    pattern.add_command(pyembroidery.END)

    # 6. التأكد من وجود مجلد الإخراج
    ensure_output_dir(output_path.parent)

    # 7. الكتابة
    try:
        pyembroidery.write_embroidery(pattern, str(output_path))
        if output_path.exists():
            return RecoveryResult(success=True, data=output_path)
        else:
            return RecoveryResult(success=False, error="الملف لم يُكتب — سبب غير معروف")
    except Exception as e:
        return RecoveryResult(success=False, error=f"فشل كتابة DST: {e}")


def write_format(stitch_list: list, output_path: Path, fmt: str = "dst") -> RecoveryResult:
    """يكتب أي صيغة تطريز — DST، PES، JEF، VP3"""
    fmt_map = {
        "dst": ".dst", "pes": ".pes", "jef": ".jef",
        "vp3": ".vp3", "exp": ".exp", "xxx": ".xxx"
    }
    ext = fmt_map.get(fmt.lower(), ".dst")
    final_path = output_path.with_suffix(ext)
    return write_dst(stitch_list, final_path)
