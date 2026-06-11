# ============================================================
#  Handler – Quản lý thời khóa biểu
#  Lệnh: /schedule, /addsubject, /timetable
# ============================================================

from telegram import Update
from telegram.ext import ContextTypes


async def schedule_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    /schedule — Xem thời khóa biểu hôm nay.
    """
    # TODO: Gọi api.get_schedule_today(telegram_id)
    await update.message.reply_text(
        "📅 *Thời khóa biểu hôm nay*\n\n"
        "_(Tính năng đang phát triển...)_",
        parse_mode="Markdown"
    )


async def addsubject_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    /addsubject — Thêm môn học mới.
    """
    # TODO: Conversation handler để hỏi tên môn, phòng, giờ học
    await update.message.reply_text(
        "➕ *Thêm môn học*\n\n"
        "_(Tính năng đang phát triển...)_",
        parse_mode="Markdown"
    )


async def timetable_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    /timetable — Xem toàn bộ thời khóa biểu theo tuần.
    """
    # TODO: Gọi api.get_timetable(telegram_id) → format bảng theo tuần
    await update.message.reply_text(
        "🗓️ *Thời khóa biểu tuần này*\n\n"
        "_(Tính năng đang phát triển...)_",
        parse_mode="Markdown"
    )
