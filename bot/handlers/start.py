# ============================================================
#  Handler cho lệnh /start
# ============================================================

from telegram import Update
from telegram.ext import ContextTypes
from services.api_client import api


async def start_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Xử lý lệnh /start.
    Đăng ký user vào hệ thống rồi gửi lời chào.
    """
    user = update.effective_user

    # Gọi Java API để đăng ký hoặc cập nhật user
    await api.register_user(
        telegram_id=user.id,
        username=user.username or "",
        full_name=user.full_name or user.first_name,
    )

    # Gửi lời chào
    await update.message.reply_text(
        f"👋 Xin chào *{user.first_name}*!\n\n"
        "🤖 Mình là *HUSTStudy Bot* — trợ lý học tập của bạn.\n\n"
        "📚 Mình có thể giúp:\n"
        "• /schedule — Xem thời khóa biểu hôm nay\n"
        "• /deadline — Xem deadline sắp tới\n"
        "• /exam — Xem lịch thi\n"
        "• /addexpense — Ghi chi tiêu\n"
        "• /report — Báo cáo tháng này\n"
        "• /quiz — Ôn từ vựng\n\n"
        "Gõ /help để xem hướng dẫn chi tiết.",
        parse_mode="Markdown"
    )
