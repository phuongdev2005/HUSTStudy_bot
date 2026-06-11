# ============================================================
#  Handler – Xuất dữ liệu ra Google Sheets
#  Lệnh: /export schedule | expense | all
# ============================================================

from telegram import Update
from telegram.ext import ContextTypes


async def export_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    /export [schedule|expense|all]
    Xuất dữ liệu ra Google Sheets.

    Ví dụ:
        /export schedule  → Xuất thời khóa biểu
        /export expense   → Xuất báo cáo chi tiêu
        /export all       → Xuất toàn bộ dữ liệu
    """
    args = context.args
    target = args[0].lower() if args else "all"

    # TODO: Gọi api.export_to_sheets(telegram_id, target)
    #       Nhận về Google Sheets URL → gửi lại cho user
    await update.message.reply_text(
        f"📤 *Xuất dữ liệu ra Google Sheets*\n\n"
        f"Loại: `{target}`\n\n"
        "_(Tính năng đang phát triển...)_",
        parse_mode="Markdown"
    )
