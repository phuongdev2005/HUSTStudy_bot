# ============================================================
#  Handler – Deadline bài tập
#  Lệnh: /deadline, /adddeadline
# ============================================================

from telegram import Update
from telegram.ext import ContextTypes


async def deadline_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    /deadline — Xem danh sách deadline sắp tới.
    """
    # TODO: Gọi api.get_upcoming_deadlines(telegram_id)
    await update.message.reply_text(
        "⏰ *Deadline sắp tới*\n\n"
        "_(Tính năng đang phát triển...)_",
        parse_mode="Markdown"
    )


async def adddeadline_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    /adddeadline — Thêm deadline bài tập mới.
    Ví dụ: /adddeadline Báo cáo Linux 2025-06-15
    """
    # TODO: Parse args → gọi api.add_deadline(telegram_id, title, due_date)
    await update.message.reply_text(
        "➕ *Thêm deadline*\n\n"
        "_(Tính năng đang phát triển...)_",
        parse_mode="Markdown"
    )
