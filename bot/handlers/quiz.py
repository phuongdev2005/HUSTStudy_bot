# ============================================================
#  Handler – Hỏi đáp từ vựng & ngữ pháp
#  Lệnh: /quiz, /addword
# ============================================================

from telegram import Update
from telegram.ext import ContextTypes


async def quiz_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    /quiz — Bắt đầu phiên ôn tập từ vựng / ngữ pháp.
    Bot sẽ hỏi từng câu, chấm điểm và thống kê kết quả.
    """
    # TODO: Gọi quiz_engine.start_session(telegram_id)
    await update.message.reply_text(
        "🧠 *Ôn tập từ vựng & ngữ pháp*\n\n"
        "_(Tính năng đang phát triển...)_",
        parse_mode="Markdown"
    )


async def addword_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    /addword — Thêm từ vựng mới vào danh sách.
    Ví dụ: /addword apple - quả táo
    """
    # TODO: Parse "word - meaning" → gọi api.add_vocabulary(telegram_id, word, meaning)
    await update.message.reply_text(
        "➕ *Thêm từ vựng*\n\n"
        "_(Tính năng đang phát triển...)_",
        parse_mode="Markdown"
    )
