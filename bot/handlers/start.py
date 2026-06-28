# ============================================================
#  Handler cho lệnh /start
# ============================================================

from telegram import Update
from telegram.ext import ContextTypes

from services.api_client import api
from handlers.menu import MAIN_KEYBOARD


async def start_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Xử lý lệnh /start.
    Đăng ký user vào hệ thống và hiện keyboard menu.
    """
    user = update.effective_user

    try:
        await api.register_user(
            telegram_id=user.id,
            username=user.username or "",
            full_name=user.full_name or user.first_name,
        )
        greeting = (
            f"👋 Xin chào *{user.first_name}*!\n\n"
            "🤖 Mình là *HUSTStudy Bot* — trợ lý học tập & tài chính của bạn.\n\n"
            "👇 *Chọn chức năng bên dưới để bắt đầu:*\n\n"
            "📅 *Lịch học* — xem TKB lớp & lịch sinh hoạt\n"
            "💸 *Chi tiêu* — ghi thu chi, scan hóa đơn & xem báo cáo\n"
            "📆 *Sự kiện* — xem deadline, lịch thi, sự kiện HUST\n"
            "🇬🇧 *Tiếng Anh* — ôn từ vựng & quiz học tập\n"
            "⚙️ *Cài đặt* — thông báo lịch, Google Sheet, API Key\n\n"
            "_Hoặc gửi ảnh hóa đơn để scan tự động!_ 📷"
        )
    except Exception:
        greeting = (
            f"⚠️ Xin chào *{user.first_name}*!\n\n"
            "Có lỗi kết nối server. Thử lại sau hoặc liên hệ admin."
        )

    await update.message.reply_text(
        greeting,
        parse_mode="Markdown",
        reply_markup=MAIN_KEYBOARD,
    )
