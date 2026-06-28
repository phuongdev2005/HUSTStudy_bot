# ============================================================
#  Handler – Lịch thi
#  /exam — Xem lịch thi sắp tới
#  /addexam <môn> <YYYY-MM-DD> <HH:MM> [phòng] [hình thức]
# ============================================================

import logging
from datetime import date, datetime
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes

from services.api_client import api
from handlers.menu import MAIN_KEYBOARD

logger = logging.getLogger(__name__)


def _days_to_exam(exam_date_str: str) -> int:
    try:
        d = date.fromisoformat(exam_date_str)
        return (d - date.today()).days
    except Exception:
        return 999


def _format_exam_list(exams: list[dict]) -> str:
    if not exams:
        return "🎉 Không có lịch thi nào sắp tới!\n\nThêm bằng lệnh `/addexam`."

    lines = ["📋 *Lịch thi sắp tới*\n"]
    for exam in exams:
        days    = _days_to_exam(exam.get("examDate", ""))
        subject = exam.get("subject", "?")
        ex_date = exam.get("examDate", "?")
        time    = exam.get("startTime", "?")[:5] if exam.get("startTime") else "?"
        room    = exam.get("room") or "Chưa có phòng"
        etype   = exam.get("examType") or ""
        dur     = exam.get("durationMinutes")
        note    = exam.get("note") or ""

        if days < 0:
            icon = "✅"
            day_text = f"Đã thi {abs(days)} ngày trước"
        elif days == 0:
            icon = "🆘"
            day_text = "🔥 HÔM NAY!"
        elif days <= 3:
            icon = "🔴"
            day_text = f"Còn {days} ngày"
        elif days <= 7:
            icon = "🟡"
            day_text = f"Còn {days} ngày"
        else:
            icon = "🟢"
            day_text = f"Còn {days} ngày"

        dur_text = f"  ⏱ {dur} phút\n" if dur else ""
        type_text = f"  📝 {etype}\n" if etype else ""
        note_text = f"  💬 {note}\n" if note else ""

        lines.append(
            f"{icon} *{subject}*\n"
            f"  📅 {ex_date}  |  🕐 {time}\n"
            f"  📍 {room}\n"
            f"{type_text}{dur_text}{note_text}"
            f"  _{day_text}_"
        )
    return "\n\n".join(lines)


async def exam_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """/exam — Xem danh sách lịch thi sắp tới."""
    tid = update.effective_user.id
    try:
        exams = await api.get_exams(tid)
        text  = _format_exam_list(exams)
        kb = InlineKeyboardMarkup([[
            InlineKeyboardButton("➕ Thêm lịch thi", callback_data="exam_add_hint"),
            InlineKeyboardButton("🔄 Làm mới",        callback_data="exam_refresh"),
        ]])
        await update.message.reply_text(text, parse_mode="Markdown", reply_markup=kb)
    except Exception as e:
        logger.error("exam_handler: %s", e)
        await update.message.reply_text(
            "❌ Lỗi tải lịch thi.\n\nDùng /start để đăng ký trước.",
            reply_markup=MAIN_KEYBOARD
        )


async def addexam_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """/addexam <môn học> <YYYY-MM-DD> <HH:MM> [phòng] [hình thức]
    Ví dụ:
      /addexam Cấu trúc dữ liệu 2025-06-20 07:00
      /addexam Giải tích 1 2025-06-22 13:00 A305 Tự luận
    """
    tid  = update.effective_user.id
    args = context.args or []

    if len(args) < 3:
        await update.message.reply_text(
            "📝 *Thêm lịch thi*\n\n"
            "Cú pháp:\n"
            "`/addexam <môn học> <YYYY-MM-DD> <HH:MM> [phòng] [hình thức]`\n\n"
            "Ví dụ:\n"
            "• `/addexam Giải tích 1 2025-06-22 07:00`\n"
            "• `/addexam CSDL 2025-06-25 13:00 A305 Tự luận`",
            parse_mode="Markdown",
        )
        return

    # Tìm vị trí ngày (YYYY-MM-DD) và giờ (HH:MM)
    date_idx = time_idx = None
    for i, arg in enumerate(args):
        try:
            date.fromisoformat(arg)
            date_idx = i
            break
        except ValueError:
            pass

    if date_idx is None:
        await update.message.reply_text(
            "❌ Không tìm thấy ngày hợp lệ (YYYY-MM-DD).",
            parse_mode="Markdown"
        )
        return

    # Tìm giờ sau ngày
    for i in range(date_idx + 1, len(args)):
        if ":" in args[i]:
            time_idx = i
            break

    if time_idx is None:
        await update.message.reply_text(
            "❌ Không tìm thấy giờ thi (HH:MM). Ví dụ: `07:00`",
            parse_mode="Markdown"
        )
        return

    subject  = " ".join(args[:date_idx])
    ex_date  = args[date_idx]
    ex_time  = args[time_idx]
    rest     = args[time_idx + 1:]
    room     = rest[0] if len(rest) > 0 else None
    ex_type  = " ".join(rest[1:]) if len(rest) > 1 else None

    if not subject:
        await update.message.reply_text("❌ Tên môn không được để trống.")
        return

    try:
        await api.add_exam(tid, subject, ex_date, ex_time, room, ex_type)
        days = _days_to_exam(ex_date)
        await update.message.reply_text(
            f"✅ *Đã thêm lịch thi!*\n\n"
            f"📖 *{subject}*\n"
            f"📅 {ex_date}  🕐 {ex_time}\n"
            + (f"📍 Phòng: {room}\n" if room else "")
            + (f"📝 {ex_type}\n" if ex_type else "")
            + (f"⏱ Còn {days} ngày" if days >= 0 else "⚠️ Ngày đã qua!"),
            parse_mode="Markdown",
        )
    except Exception as e:
        logger.error("addexam_handler: %s", e)
        await update.message.reply_text(f"❌ Lỗi: {e}")


async def exam_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Inline keyboard callbacks cho lịch thi."""
    query = update.callback_query
    await query.answer()
    tid = query.from_user.id

    if query.data == "exam_refresh":
        try:
            exams = await api.get_exams(tid)
            text  = _format_exam_list(exams)
            kb = InlineKeyboardMarkup([[
                InlineKeyboardButton("➕ Thêm lịch thi", callback_data="exam_add_hint"),
                InlineKeyboardButton("🔄 Làm mới",        callback_data="exam_refresh"),
            ]])
            await query.edit_message_text(text, parse_mode="Markdown", reply_markup=kb)
        except Exception as e:
            await query.edit_message_text(f"❌ Lỗi: {e}")

    elif query.data == "exam_add_hint":
        await query.edit_message_text(
            "📝 *Thêm lịch thi mới*\n\n"
            "`/addexam <môn học> <YYYY-MM-DD> <HH:MM> [phòng] [hình thức]`\n\n"
            "Ví dụ:\n"
            "• `/addexam Giải tích 1 2025-06-22 07:00`\n"
            "• `/addexam CSDL 2025-06-25 13:00 A305 Tự luận`",
            parse_mode="Markdown",
        )
