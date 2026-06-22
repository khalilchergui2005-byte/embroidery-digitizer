# تجميع الألوان — K-Means لتقليل ألوان الصورة لعدد مناسب للتطريز
import numpy as np
from sklearn.cluster import KMeans
from PIL import Image
import io
from config.constants import MAX_COLORS
from infra.error_recovery.base_recovery import RecoveryResult


def extract_colors(image_bytes: bytes, n_colors: int = 6) -> RecoveryResult:
    """
    يستخرج أهم الألوان من الصورة بـ K-Means
    المدخل: bytes الصورة + عدد الألوان المطلوب
    المخرج: قائمة ألوان RGB مرتبة حسب الأهمية
    """
    # التحقق من عدد الألوان
    if n_colors > MAX_COLORS:
        n_colors = MAX_COLORS

    try:
        # فتح الصورة وتحويلها لـ RGB
        img = Image.open(io.BytesIO(image_bytes)).convert("RGB")

        # تصغير للسرعة — K-Means بطيء على صور كبيرة
        img.thumbnail((200, 200))
        pixels = np.array(img).reshape(-1, 3).astype(float)

        # تشغيل K-Means
        kmeans = KMeans(n_clusters=n_colors, random_state=42, n_init=10)
        kmeans.fit(pixels)

        # الألوان المستخرجة + نسبة كل لون
        centers = kmeans.cluster_centers_.astype(int)
        labels = kmeans.labels_
        counts = np.bincount(labels)
        total = len(labels)

        colors = []
        for i, (center, count) in enumerate(zip(centers, counts)):
            colors.append({
                "id": i,
                "rgb": tuple(center.tolist()),
                "hex": "#{:02x}{:02x}{:02x}".format(*center),
                "percentage": round(count / total * 100, 1)
            })

        # ترتيب حسب النسبة — الأكثر أولاً
        colors.sort(key=lambda x: x["percentage"], reverse=True)

        return RecoveryResult(success=True, data=colors)

    except Exception as e:
        return RecoveryResult(success=False, error=f"فشل استخراج الألوان: {e}")


def reduce_colors(image_bytes: bytes, n_colors: int = 6) -> RecoveryResult:
    """يعيد الصورة بعدد ألوان محدد — يبسّط الصورة للتطريز"""
    try:
        img = Image.open(io.BytesIO(image_bytes)).convert("RGB")
        # استخدام quantize لتقليل الألوان
        quantized = img.quantize(colors=n_colors, method=Image.Quantize.MEDIANCUT)
        quantized_rgb = quantized.convert("RGB")

        buffer = io.BytesIO()
        quantized_rgb.save(buffer, format="PNG")
        return RecoveryResult(success=True, data=buffer.getvalue())

    except Exception as e:
        return RecoveryResult(success=False, error=f"فشل تقليل الألوان: {e}")
