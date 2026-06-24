# معالجة الرسائل الواردة — يربط Telegram بالـ pipeline
import io
import logging
import uuid
from pathlib import Path

from telegram import Update
from telegram.ext import ContextTypes

from layers.layer0_input.ingestion import ingest_image
from layers.layer1_image.background_sep import separate_background
from layers.layer2_color.color_cluster import extract_colors
from layers.layer7_output.dst_writer import write_dst

# مجلد الإخراج
OUTPUT_DIR = Path("outputs")
OUTPUT_DIR.mkdir(exist_ok=True)

logger = logging.getLogger(__name__)


def _build_simple_stitches(colors: list, width: int, height: int) -> list:
    """
    يبني غرزات بسيطة من الألوان — كل لون = شريط أفقي
    MVP مؤقت — يُستبدل لاحقاً بـ Gemini + digitizing engine
    """
    stitches = []
    if not colors:
        return stitches

    scale = 1000
    n_colors = len(colors)
    strip_height = scale // max(n_colors, 1)

    for i, color_info in enumerate(colors):
        rgb = color_info["rgb"]
        y_start = i * strip_height
        y_end = y_start + strip_height

        stitches.append({
            "type": "jump",
            "x": 0,
            "y": y_start,
            "color": rgb,
            "length_mm": 0,
        })

        x = 0
        step = 40
        direction = 1

        while y_start < y_end:
            while 0 <= x <= scale:
                stitches.append({
                    "type": "stitch",
                    "x": x,
                    "y": y_start,
                    "color": rgb,
                    "length_mm": 4.0,
                })
                x += step * direction

            y_start += step
            direction *= -1
            x = max(0, min(x, scale))

    return stitches


async def handle_image(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """يستقبل صورة ويعيد ملف DST — يعمل مع photo و document"""
    user_id = update.effective_user.id
    logger.info(f"صورة واردة من المستخدم: {user_id}")

    wait_msg = await update.message.reply_text(
        "جارٍ المعالجة... انتظر لحظة",
        do_quote=True
    )

    try:
        if update.message.photo:
            file_obj = await update.message.photo[-1].get_file()
            filename = f"photo_{user_id}.jpg"
        elif update.message.document:
            doc = update.message.document
            file_obj = await doc.get_file()
            filename = doc.file_name or f"doc_{user_id}.jpg"
        else:
            await wait_msg.edit_text("لم أتعرف على نوع الملف. أرسل صورة.")
            return

        buffer = io.BytesIO()
        await file_obj.download_to_memory(buffer)
        image_bytes = buffer.getvalue()
        logger.info(f"حجم الصورة: {len(image_bytes) / 1024:.1f} KB")

        ingest_result = ingest_image(image_bytes, filename)
        if not ingest_result.success:
            await wait_msg.edit_text(
                f"خطأ: {ingest_result.error}\n\n"
                "تأكد أن الصورة واضحة وحجمها أقل من 10MB"
            )
            return

        width = ingest_result.data["width"]
        height = ingest_result.data.get("height", width)

        await wait_msg.edit_text("جارٍ فصل الخلفية...")
        bg_result = separate_background(image_bytes, edge_count=0)
        if not bg_result.success:
            await wait_msg.edit_text(f"فشل فصل الخلفية: {bg_result.error}")
            return

        clean_bytes = bg_result.data
        if bg_result.used_fallback:
            logger.warning(f"استُخدم GrabCut fallback للمستخدم {user_id}")

        await wait_msg.edit_text("جارٍ تحليل الألوان...")
        color_result = extract_colors(clean_bytes, n_colors=6)
        if not color_result.success:
            await wait_msg.edit_text(f"فشل تحليل الألوان: {color_result.error}")
            return

        colors = color_result.data
        logger.info(f"ألوان مستخرجة: {len(colors)}")

        await wait_msg.edit_text("جارٍ توليد الغرزات...")
        stitches = _build_simple_stitches(colors, width, height)

        if not stitches:
            await wait_msg.edit_text("لم أتمكن من توليد غرزات من هذه الصورة.")
            return

        job_id = uuid.uuid4().hex[:8]
        output_path = OUTPUT_DIR / f"rash_{user_id}_{job_id}.dst"

        dst_result = write_dst(
            stitch_list=stitches,
            output_path=output_path,
            metadata={"name": f"rash_{job_id}", "author": "embroidery-digitizer"}
        )

        if not dst_result.success:
            await wait_msg.edit_text(f"فشل توليد الملف: {dst_result.error}")
            return

        await wait_msg.edit_text("جاهز! جارٍ الإرسال...")

        caption = (
            f"ملف الرشمة جاهز!\n\n"
            f"الغرزات: {len(stitches):,}\n"
            f"الألوان: {len(colors)}\n"
            f"الصيغة: DST (Tajima)\n\n"
            f"ملف MVP تجريبي — راجعه على برنامج التطريز قبل التشغيل"
        )

        with open(output_path, "rb") as f:
            await update.message.reply_document(
                document=f,
                filename=output_path.name,
                caption=caption,
                do_quote=True
            )

        await wait_msg.delete()
        logger.info(f"ملف أُرسل للمستخدم {user_id}: {output_path.name}")

    except Exception as e:
        logger.error(f"خطأ غير متوقع للمستخدم {user_id}: {e}", exc_info=True)
        try:
            await wait_msg.edit_text(
                "حدث خطأ غير متوقع.\n"
                "أرسل الصورة مرة ثانية أو تواصل مع الدعم."
            )
        except Exception:
            pass


async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """يرد على الرسائل النصية بتوجيه لإرسال صورة"""
    await update.message.reply_text(
        "أرسل صورة التصميم للبدء.\n\n"
        "للحصول على أفضل نتيجة:\n"
        "- خلفية بيضاء نظيفة\n"
        "- إضاءة جيدة\n"
        "- الصورة واضحة وغير ضبابية",
        do_quote=True
    )
