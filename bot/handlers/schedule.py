# ============================================================
#  Handler – Thời khóa biểu từ Google Sheet cá nhân
#  Lệnh: /schedule, /setsheet, /syncsheet
# ============================================================

import logging
from telegram import Update
from telegram.ext import ContextTypes

from services.api_client import api

logger = logging.getLogger(__name__)

# Tên thứ trong tuần (dayOfWeek: 1=T2 … 7=CN)
DAY_NAMES = {1: "Thứ 2", 2: "Thứ 3", 3: "Thứ 4",
             4: "Thứ 5", 5: "Thứ 6", 6: "Thứ 7", 7: "Chủ nhật"}


# ── /schedule — Xem lịch hôm nay ──────────────────────────────

async def schedule_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    /schedule — Hiển thị thời khóa biểu hôm nay từ DB.
    Dữ liệu được sync từ Google Sheet của user.
    """
    telegram_id = update.effective_user.id

    try:
        sessions = await api.get_today_schedule(telegram_id)

        if not sessions:
            await update.message.reply_text(
                "📅 *Hôm nay không có lịch học* 🎉\n\n"
                "Nếu bạn chưa liên kết Google Sheet, hãy dùng:\n"
                "`/setsheet <link sheet của bạn>`",
                parse_mode="Markdown"
            )
            return

        # Format hiển thị
        lines = ["📅 *Thời khóa biểu hôm nay*\n"]
        for s in sessions:
            room_str = f" — 📍 {s['room']}" if s.get("room") else ""
            teacher_str = f"\n   👨‍🏫 {s['teacher']}" if s.get("teacher") else ""
            lines.append(
                f"⏰ `{s['startTime']} – {s['endTime']}`\n"
                f"   📚 *{s['subjectName']}*{room_str}{teacher_str}"
            )

        await update.message.reply_text(
            "\n\n".join(lines),
            parse_mode="Markdown"
        )

    except Exception as e:
        logger.error("Lỗi get_today_schedule user %d: %s", telegram_id, e)
        await update.message.reply_text(
            "⚠️ Không thể lấy lịch học. Backend chưa hoạt động hoặc bạn chưa đăng ký.\n"
            "Dùng /start để đăng ký tài khoản."
        )


# ── /setsheet — Liên kết Google Sheet ─────────────────────────

async def setsheet_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    /setsheet <link> — Lưu link Google Sheet cá nhân của user.

    Cú pháp: /setsheet https://docs.google.com/spreadsheets/d/...
    """
    telegram_id = update.effective_user.id

    # Kiểm tra user có truyền link không
    if not context.args:
        await update.message.reply_text(
            "📋 *Cách dùng lệnh /setsheet*\n\n"
            "```\n/setsheet <link Google Sheet của bạn>\n```\n\n"
            "*Ví dụ:*\n"
            "`/setsheet https://docs.google.com/spreadsheets/d/abc123.../edit`\n\n"
            "━━━━━━━━━━━━━━━━━━━━━━━\n"
            "📌 *Format sheet (từ hàng 2):*\n"
            "```\n"
            "Tên môn  | Mã môn | Thứ | Giờ bắt | Giờ kết | Phòng | GV\n"
            "Giải tích| MA1010 | 2   | 07:00   | 09:30   | B1-301| Thầy A\n"
            "```\n"
            "⚠️ Sheet phải để chế độ *'Anyone with the link can view'*",
            parse_mode="Markdown"
        )
        return

    sheet_url = context.args[0].strip()

    try:
        result = await api.set_sheet(telegram_id, sheet_url)
        await update.message.reply_text(
            result.get("message", "✅ Đã lưu sheet!"),
            parse_mode="Markdown"
        )
    except Exception as e:
        logger.error("Lỗi set_sheet user %d: %s", telegram_id, e)
        await update.message.reply_text(
            "⚠️ Không thể lưu link sheet. Backend chưa hoạt động.\n"
            "Dùng /start để đăng ký tài khoản trước."
        )


# ── /syncsheet — Đồng bộ dữ liệu từ Sheet ────────────────────

async def syncsheet_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    /syncsheet — Đọc Google Sheet của user và đồng bộ vào DB.
    """
    telegram_id = update.effective_user.id

    # Hiện thông báo đang xử lý
    msg = await update.message.reply_text("⏳ Đang đồng bộ từ Google Sheet...")

    try:
        result = await api.sync_sheet(telegram_id)

        text = result.get("message", "Hoàn thành.")

        # Hiển thị danh sách lỗi nếu có
        errors = result.get("errors", [])
        if errors:
            error_lines = "\n".join(f"• {e}" for e in errors[:5])  # Tối đa 5 lỗi
            text += f"\n\n⚠️ *Dòng bị bỏ qua:*\n{error_lines}"
            if len(errors) > 5:
                text += f"\n_...và {len(errors) - 5} dòng lỗi khác_"

        if result.get("success"):
            text += "\n\nDùng /schedule để xem lịch hôm nay 📅"

        await msg.edit_text(text, parse_mode="Markdown")

    except Exception as e:
        logger.error("Lỗi sync_sheet user %d: %s", telegram_id, e)
        await msg.edit_text(
            "⚠️ Không thể đồng bộ. Backend chưa hoạt động.\n"
            "Dùng /start để đăng ký tài khoản trước."
        )


# ── /timetable — Xem lịch cả tuần ────────────────────────────

async def timetable_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    /timetable — Hiển thị thời khóa biểu cả tuần.
    """
    telegram_id = update.effective_user.id

    try:
        sessions = await api.get_week_schedule(telegram_id)

        if not sessions:
            await update.message.reply_text(
                "🗓️ *Chưa có thời khóa biểu*\n\n"
                "1️⃣ Liên kết sheet: `/setsheet <link>`\n"
                "2️⃣ Đồng bộ: `/syncsheet`",
                parse_mode="Markdown"
            )
            return

        # Nhóm theo thứ
        by_day: dict[int, list] = {}
        for s in sessions:
            day = s["dayOfWeek"]
            by_day.setdefault(day, []).append(s)

        lines = ["🗓️ *Thời khóa biểu tuần này*\n"]
        for day in sorted(by_day.keys()):
            lines.append(f"*{DAY_NAMES.get(day, f'Thứ {day}')}*")
            for s in by_day[day]:
                room_str = f" ({s['room']})" if s.get("room") else ""
                lines.append(f"  ⏰ `{s['startTime']}–{s['endTime']}` {s['subjectName']}{room_str}")
            lines.append("")  # Dòng trống giữa các ngày

        await update.message.reply_text(
            "\n".join(lines).rstrip(),
            parse_mode="Markdown"
        )

    except Exception as e:
        logger.error("Lỗi get_week_schedule user %d: %s", telegram_id, e)
        await update.message.reply_text(
            "⚠️ Không thể lấy lịch học. Backend chưa hoạt động."
        )
