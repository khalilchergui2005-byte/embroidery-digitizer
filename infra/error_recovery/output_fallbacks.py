# fallbacks المخرجات — عند فشل كتابة الملف النهائي
from pathlib import Path
from infra.error_recovery.base_recovery import RecoveryResult


def fallback_output_path(original_path: Path, suffix: str = "_fallback") -> Path:
    """يُنشئ مسار بديل عند فشل الكتابة في المسار الأصلي"""
    return original_path.parent / (original_path.stem + suffix + original_path.suffix)


def ensure_output_dir(output_dir: Path) -> RecoveryResult:
    """يتأكد من وجود مجلد المخرجات — يُنشئه إن لم يوجد"""
    try:
        output_dir.mkdir(parents=True, exist_ok=True)
        return RecoveryResult(success=True, data=output_dir)
    except Exception as e:
        return RecoveryResult(success=False, error=str(e))


def safe_write_file(path: Path, data: bytes) -> RecoveryResult:
    """يكتب ملفاً بأمان — يحاول المسار البديل عند الفشل"""
    # المحاولة الأولى: المسار الأصلي
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)
        return RecoveryResult(success=True, data=path)
    except Exception as e:
        pass

    # المحاولة الثانية: مسار بديل
    try:
        fallback_path = fallback_output_path(path)
        fallback_path.write_bytes(data)
        return RecoveryResult(
            success=True,
            data=fallback_path,
            error=f"كُتب في المسار البديل: {fallback_path}",
            used_fallback=True
        )
    except Exception as e:
        return RecoveryResult(success=False, error=f"فشل الكتابة كلياً: {e}")


def check_disk_space(path: Path, required_mb: float = 10.0) -> RecoveryResult:
    """يتحقق من توفر مساحة كافية قبل الكتابة"""
    try:
        import shutil
        free_bytes = shutil.disk_usage(path.parent).free
        free_mb = free_bytes / (1024 * 1024)
        if free_mb < required_mb:
            return RecoveryResult(
                success=False,
                error=f"مساحة غير كافية: {free_mb:.1f}MB متاح، مطلوب {required_mb}MB"
            )
        return RecoveryResult(success=True, data=free_mb)
    except Exception as e:
        return RecoveryResult(success=False, error=str(e))
