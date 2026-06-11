# ============================================================
#  Handler – Lịch thi
#  Lệnh: /exam, /addexam
# ============================================================

from telegram import Update
from telegram.ext import ContextTypes


async def exam_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    /exam — Xem danh sách lịch thi sắp tới.
    Hiển thị: môn thi, phòng thi, ngày giờ thi.
    """
    # TODO: Gọi api.get_upcoming_exams(telegram_id)
    await update.message.reply_text(
        "📝 *Lịch thi sắp tới*\n\n"
        "_(Tính năng đang phát triển...)_",
        parse_mode="Markdown"
    )


async def addexam_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    /addexam — Thêm lịch thi mới.
    Ví dụ: /addexam "Cấu trúc dữ liệu" A305 2025-06-20 07:00
    """
    # TODO: Parse args → gọi api.add_exam(telegram_id, subject, room, datetime)
    await update.message.reply_text(
        "➕ *Thêm lịch thi*\n\n"
        "_(Tính năng đang phát triển...)_",
        parse_mode="Markdown"
    )
