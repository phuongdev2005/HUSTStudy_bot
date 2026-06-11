# ============================================================
#  HUSTStudy Telegram Bot – Entry Point
#  Khởi động bot và đăng ký tất cả handlers
# ============================================================

import logging
from telegram import BotCommand
from telegram.ext import Application, CommandHandler

from config import BOT_TOKEN
from handlers.start import start_handler
from handlers.schedule import (
    schedule_handler,
    setsheet_handler,
    syncsheet_handler,
    timetable_handler,
)
from services.api_client import api

# Cấu hình logging — xem log khi bot chạy
logging.basicConfig(
    format="%(asctime)s [%(levelname)s] %(name)s – %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)


async def post_init(application: Application) -> None:
    """
    Chạy sau khi bot khởi động.
    Đăng ký menu lệnh hiển thị trong Telegram.
    """
    await application.bot.set_my_commands([
        BotCommand("start",      "Bắt đầu & đăng ký tài khoản"),
        BotCommand("schedule",   "Xem thời khóa biểu hôm nay"),
        BotCommand("timetable",  "Xem lịch học cả tuần"),
        BotCommand("setsheet",   "Liên kết Google Sheet cá nhân"),
        BotCommand("syncsheet",  "Đồng bộ thời khóa biểu từ Sheet"),
        BotCommand("deadline",   "Xem deadline sắp tới"),
        BotCommand("exam",       "Xem lịch thi"),
        BotCommand("addexpense", "Ghi chi tiêu"),
        BotCommand("addincome",  "Ghi thu nhập"),
        BotCommand("report",     "Báo cáo chi tiêu tháng này"),
        BotCommand("quiz",       "Ôn từ vựng tiếng Anh"),
        BotCommand("help",       "Hướng dẫn sử dụng"),
    ])
    logger.info("✅ Bot commands menu đã được cập nhật")


async def post_shutdown(application: Application) -> None:
    """Dọn dẹp khi bot tắt."""
    await api.close()
    logger.info("Bot đã tắt.")


def main():
    logger.info("🚀 Đang khởi động HUSTStudy Bot...")

    app = (
        Application.builder()
        .token(BOT_TOKEN)
        .post_init(post_init)
        .post_shutdown(post_shutdown)
        .build()
    )

    # ── Đăng ký handlers ──────────────────────────────────────────
    app.add_handler(CommandHandler("start",      start_handler))
    # ── Schedule / Google Sheet ────────────────────────────────
    app.add_handler(CommandHandler("schedule",   schedule_handler))
    app.add_handler(CommandHandler("timetable",  timetable_handler))
    app.add_handler(CommandHandler("setsheet",   setsheet_handler))
    app.add_handler(CommandHandler("syncsheet",  syncsheet_handler))

    # ── Chạy bot (polling) ────────────────────────────────────
    logger.info("Bot đang chạy... Nhấn Ctrl+C để dừng.")
    app.run_polling(drop_pending_updates=True)


if __name__ == "__main__":
    main()
