# ============================================================
#  Scheduler – Gửi thông báo tự động
#  Dùng APScheduler để chạy các tác vụ định kỳ
# ============================================================

import logging
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

logger = logging.getLogger(__name__)

# Scheduler instance dùng chung toàn bộ bot
scheduler = AsyncIOScheduler(timezone="Asia/Ho_Chi_Minh")


def start_scheduler(bot):
    """
    Khởi động scheduler và đăng ký các job định kỳ.
    Gọi hàm này trong post_init của Application.
    """
    # TODO: Thêm các job nhắc lịch học, deadline, thi, tổng hợp ngày

    # Ví dụ: Gửi tổng hợp ngày lúc 7:00 sáng mỗi ngày
    # scheduler.add_job(
    #     send_daily_summary,
    #     CronTrigger(hour=7, minute=0),
    #     args=[bot],
    #     id="daily_summary",
    #     replace_existing=True,
    # )

    scheduler.start()
    logger.info("✅ Scheduler đã khởi động")


async def send_daily_summary(bot):
    """
    Gửi bản tổng hợp sự kiện học tập trong ngày cho tất cả user.
    - Lịch học hôm nay
    - Deadline sắp tới
    - Lịch thi gần nhất
    """
    # TODO: Lấy danh sách user từ api → gửi tin nhắn tổng hợp
    logger.info("📅 Đang gửi daily summary...")


async def send_class_reminder(bot, telegram_id: int, subject: str, time: str):
    """Nhắc giờ học trước N phút."""
    await bot.send_message(
        chat_id=telegram_id,
        text=f"⏰ *Nhắc lịch học*\n\n"
             f"🏫 {subject} bắt đầu lúc *{time}*",
        parse_mode="Markdown"
    )


async def send_deadline_reminder(bot, telegram_id: int, title: str, days_left: int):
    """Nhắc deadline bài tập."""
    await bot.send_message(
        chat_id=telegram_id,
        text=f"⚠️ *Nhắc deadline*\n\n"
             f"📌 {title}\n"
             f"Còn *{days_left} ngày* nữa đến hạn nộp!",
        parse_mode="Markdown"
    )


async def send_exam_reminder(bot, telegram_id: int, subject: str, room: str, days_left: int):
    """Nhắc lịch thi."""
    await bot.send_message(
        chat_id=telegram_id,
        text=f"📝 *Nhắc lịch thi*\n\n"
             f"Môn: *{subject}*\n"
             f"Phòng: *{room}*\n"
             f"Còn *{days_left} ngày* nữa!",
        parse_mode="Markdown"
    )
