# ============================================================
#  Handler – Quản lý chi tiêu cá nhân
#  Lệnh: /addexpense, /addincome, /report, /budget
# ============================================================

from telegram import Update
from telegram.ext import ContextTypes


async def addexpense_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    /addexpense <số_tiền> <ghi_chú>
    Ví dụ: /addexpense 35000 cơm trưa
    """
    # TODO: Parse args → gọi api.add_transaction(type=EXPENSE, ...)
    await update.message.reply_text(
        "💸 *Ghi chi tiêu*\n\n"
        "_(Tính năng đang phát triển...)_",
        parse_mode="Markdown"
    )


async def addincome_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    /addincome <số_tiền> <ghi_chú>
    Ví dụ: /addincome 500000 tiền học bổng
    """
    # TODO: Parse args → gọi api.add_transaction(type=INCOME, ...)
    await update.message.reply_text(
        "💰 *Ghi thu nhập*\n\n"
        "_(Tính năng đang phát triển...)_",
        parse_mode="Markdown"
    )


async def report_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    /report [today|week|month]
    Xem báo cáo chi tiêu theo khoảng thời gian.
    """
    # TODO: Gọi api.get_report(telegram_id, period) → format bảng tổng hợp
    await update.message.reply_text(
        "📊 *Báo cáo chi tiêu*\n\n"
        "_(Tính năng đang phát triển...)_",
        parse_mode="Markdown"
    )


async def budget_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    /budget — Xem ngân sách tháng và mức đã sử dụng.
    Hiển thị thanh progress bar theo từng danh mục.
    """
    # TODO: Gọi api.get_budget_status(telegram_id)
    await update.message.reply_text(
        "🎯 *Ngân sách tháng này*\n\n"
        "_(Tính năng đang phát triển...)_",
        parse_mode="Markdown"
    )
