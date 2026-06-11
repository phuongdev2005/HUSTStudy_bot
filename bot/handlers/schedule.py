# ============================================================
#  Handler – Lịch sinh hoạt hằng ngày từ Google Sheet
#  Lệnh: /schedule, /timetable, /setsheet, /syncsheet
# ============================================================

import logging
from datetime import datetime
from telegram import Update
from telegram.ext import ContextTypes

from services.api_client import api

logger = logging.getLogger(__name__)

# Emoji theo danh mục hoạt động
CATEGORY_EMOJI = {
    "Nghỉ ngơi":  "😴",
    "Sinh hoạt":  "🪥",
    "Ăn uống":    "🍜",
    "Học tập":    "📚",
    "Thể dục":    "🏃",
    "Giải trí":   "🎮",
    "Di chuyển":  "🚌",
    "Khác":       "📌",
}

# Tên thứ trong tuần (dayOfWeek: 1=T2 … 7=CN)
DAY_NAMES = {
    1: "Thứ Hai", 2: "Thứ Ba",  3: "Thứ Tư",
    4: "Thứ Năm", 5: "Thứ Sáu", 6: "Thứ Bảy", 7: "Chủ Nhật",
}


def _format_activity(item: dict) -> str:
    """Format 1 dòng hoạt động: ⏰ HH:MM – HH:MM | emoji Tên hoạt động [Ghi chú]"""
    cat   = item.get("category", "Khác")
    emoji = CATEGORY_EMOJI.get(cat, "📌")
    note  = f" _{item['note']}_" if item.get("note") else ""
    return f"`{item['startTime']}–{item['endTime']}` {emoji} *{item['activity']}*{note}"


def _today_dow() -> int:
    """Trả về day of week theo Java convention: 1=T2 … 7=CN."""
    return datetime.now().isoweekday()  # Python: 1=Mon … 7=Sun — trùng!


# ── /schedule — Timeline hôm nay ──────────────────────────────

async def schedule_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    /schedule — Hiển thị lịch sinh hoạt toàn ngày hôm nay.
    Kết hợp hoạt động "Tất cả" (mọi ngày) + hoạt động riêng ngày hôm nay.
    """
    telegram_id = update.effective_user.id
    today_name  = DAY_NAMES.get(_today_dow(), "Hôm nay")
    today_date  = datetime.now().strftime("%d/%m/%Y")

    try:
        items = await api.get_daily_schedule(telegram_id)

        if not items:
            await update.message.reply_text(
                "📅 *Chưa có lịch sinh hoạt!*\n\n"
                "Hãy tạo Google Sheet theo mẫu rồi liên kết:\n"
                "1️⃣ `/setsheet <link sheet>`\n"
                "2️⃣ `/syncsheet`\n\n"
                "📋 Xem file mẫu tại: `docs/timetable_template.csv`",
                parse_mode="Markdown"
            )
            return

        # Header
        lines = [f"📅 *Lịch {today_name}, {today_date}*\n"]

        # Phân nhóm theo danh mục để hiển thị đẹp hơn
        prev_cat = None
        for item in items:
            cat = item.get("category", "Khác")
            # Thêm separator khi chuyển nhóm danh mục lớn
            if prev_cat and prev_cat != cat and cat in ("Học tập", "Nghỉ ngơi"):
                lines.append("┈" * 20)
            lines.append(_format_activity(item))
            prev_cat = cat

        await update.message.reply_text(
            "\n".join(lines),
            parse_mode="Markdown"
        )

    except Exception as e:
        logger.error("Lỗi get_daily_schedule user %d: %s", telegram_id, e)
        await update.message.reply_text(
            "⚠️ Không thể lấy lịch. Backend chưa hoạt động hoặc bạn chưa đăng ký.\n"
            "Dùng /start để đăng ký tài khoản."
        )


# ── /timetable — Lịch cả tuần ─────────────────────────────────

async def timetable_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    /timetable — Xem lịch sinh hoạt cả tuần (nhóm theo ngày).
    """
    telegram_id = update.effective_user.id

    try:
        items = await api.get_all_daily_schedule(telegram_id)

        if not items:
            await update.message.reply_text(
                "🗓️ *Chưa có lịch sinh hoạt!*\n\n"
                "1️⃣ `/setsheet <link sheet>`\n"
                "2️⃣ `/syncsheet`",
                parse_mode="Markdown"
            )
            return

        # Nhóm: None = mọi ngày, 1–7 = ngày cụ thể
        everyday  = [i for i in items if i.get("dayOfWeek") is None]
        by_day: dict[int, list] = {}
        for i in items:
            if i.get("dayOfWeek") is not None:
                by_day.setdefault(i["dayOfWeek"], []).append(i)

        lines = ["🗓️ *Lịch sinh hoạt cả tuần*\n"]

        # Hoạt động mọi ngày
        if everyday:
            lines.append("*🔁 Mọi ngày*")
            for item in everyday:
                lines.append(f"  {_format_activity(item)}")
            lines.append("")

        # Theo từng thứ
        for day in sorted(by_day.keys()):
            lines.append(f"*📆 {DAY_NAMES.get(day, f'Thứ {day}')}*")
            for item in by_day[day]:
                lines.append(f"  {_format_activity(item)}")
            lines.append("")

        await update.message.reply_text(
            "\n".join(lines).rstrip(),
            parse_mode="Markdown"
        )

    except Exception as e:
        logger.error("Lỗi get_all_daily_schedule user %d: %s", telegram_id, e)
        await update.message.reply_text("⚠️ Không thể lấy lịch. Backend chưa hoạt động.")


# ── /setsheet — Liên kết Google Sheet ─────────────────────────

async def setsheet_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    /setsheet <link> — Lưu link Google Sheet cá nhân của user.
    """
    telegram_id = update.effective_user.id

    if not context.args:
        await update.message.reply_text(
            "📋 *Cách dùng /setsheet*\n\n"
            "`/setsheet https://docs.google.com/spreadsheets/d/...`\n\n"
            "━━━━━━━━━━━━━━━━━━━━━\n"
            "📌 *Format sheet* (từ hàng 2):\n"
            "```\n"
            "Thứ     | Bắt đầu | Kết thúc | Hoạt động       | Danh mục  | Ghi chú\n"
            "Tất cả  | 00:00   | 06:30    | Ngủ             | Nghỉ ngơi |\n"
            "Tất cả  | 06:30   | 07:00    | Vệ sinh cá nhân | Sinh hoạt |\n"
            "2       | 07:30   | 09:30    | Giải tích 1     | Học tập   | B1-301\n"
            "```\n\n"
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


# ── /syncsheet — Đồng bộ lịch sinh hoạt từ Sheet ─────────────

async def syncsheet_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    /syncsheet — Đọc Google Sheet (format 6 cột) → sync vào DB.
    """
    telegram_id = update.effective_user.id
    msg = await update.message.reply_text("⏳ Đang đồng bộ lịch sinh hoạt từ Google Sheet...")

    try:
        result = await api.sync_daily_sheet(telegram_id)

        text = result.get("message", "Hoàn thành.")

        errors = result.get("errors", [])
        if errors:
            error_lines = "\n".join(f"• {e}" for e in errors[:5])
            text += f"\n\n⚠️ *Dòng bị bỏ qua:*\n{error_lines}"
            if len(errors) > 5:
                text += f"\n_...và {len(errors) - 5} dòng lỗi khác_"

        if result.get("success"):
            text += "\n\nDùng /schedule để xem lịch hôm nay 📅"

        await msg.edit_text(text, parse_mode="Markdown")

    except Exception as e:
        logger.error("Lỗi sync_daily_sheet user %d: %s", telegram_id, e)
        await msg.edit_text(
            "⚠️ Không thể đồng bộ. Backend chưa hoạt động.\n"
            "Dùng /start để đăng ký tài khoản trước."
        )
