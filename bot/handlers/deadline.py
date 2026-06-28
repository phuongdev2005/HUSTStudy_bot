# ============================================================
#  Handler – Deadline bài tập
#  /deadline, /adddeadline <tiêu đề> <ngày YYYY-MM-DD> [môn học]
#  /donedl <id>
# ============================================================

import logging
from datetime import date, datetime, timedelta
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes

from services.api_client import api
from handlers.menu import MAIN_KEYBOARD

logger = logging.getLogger(__name__)


def _days_left(due_date_str: str) -> int:
    """Tính số ngày còn lại đến deadline."""
    try:
        due = date.fromisoformat(due_date_str)
        return (due - date.today()).days
    except Exception:
        return 999


def _urgency_icon(days: int) -> str:
    if days < 0:   return "🔴"   # Đã quá hạn
    if days == 0:  return "🆘"   # Hôm nay
    if days <= 2:  return "🔴"   # 1-2 ngày
    if days <= 7:  return "🟡"   # Tuần này
    return "🟢"                  # Còn nhiều thời gian


def _format_deadline_list(deadlines: list[dict]) -> str:
    if not deadlines:
        return "✅ Không có deadline nào! Thoải mái rồi 🎉"

    lines = ["⏰ *Deadline sắp tới*\n"]
    for dl in deadlines:
        days = _days_left(dl.get("dueDate", ""))
        icon = _urgency_icon(days)
        title   = dl.get("title", "?")
        subject = dl.get("subject") or ""
        due     = dl.get("dueDate", "?")
        done    = dl.get("isDone", False)
        dl_id   = dl.get("id", "")

        if done:
            lines.append(f"✅ ~~{title}~~ _(đã xong)_")
            continue

        if days < 0:
            day_text = f"⚠️ Quá hạn {abs(days)} ngày!"
        elif days == 0:
            day_text = "⚠️ Hôm nay!"
        elif days == 1:
            day_text = "Còn 1 ngày"
        else:
            day_text = f"Còn {days} ngày"

        subj_line = f"  📚 {subject}\n" if subject else ""
        lines.append(
            f"{icon} *{title}*\n"
            f"{subj_line}"
            f"  📅 {due}  |  {day_text}\n"
            f"  ✓ /donedl_{dl_id}"
        )
    return "\n".join(lines)


async def deadline_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """/deadline — Xem danh sách deadline sắp tới."""
    tid = update.effective_user.id
    try:
        deadlines = await api.get_deadlines(tid)
        text = _format_deadline_list(deadlines)
        kb = InlineKeyboardMarkup([[
            InlineKeyboardButton("➕ Thêm deadline", callback_data="dl_add_hint"),
            InlineKeyboardButton("🔄 Làm mới",       callback_data="dl_refresh"),
        ]])
        await update.message.reply_text(text, parse_mode="Markdown", reply_markup=kb)
    except Exception as e:
        logger.error("deadline_handler: %s", e)
        await update.message.reply_text(
            "❌ Lỗi tải deadline.\n\nDùng /start để đăng ký trước.",
            reply_markup=MAIN_KEYBOARD
        )


async def adddeadline_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """/adddeadline <tiêu đề> <YYYY-MM-DD> [môn học]
    Ví dụ:
      /adddeadline Báo cáo Linux 2025-06-20
      /adddeadline Bài tập lớn CSDL 2025-06-25 Cơ sở dữ liệu
    """
    tid = update.effective_user.id
    args = context.args or []

    if len(args) < 2:
        await update.message.reply_text(
            "📝 *Thêm deadline*\n\n"
            "Cú pháp:\n"
            "`/adddeadline <tiêu đề> <YYYY-MM-DD> [môn học]`\n\n"
            "Ví dụ:\n"
            "• `/adddeadline Báo cáo Linux 2025-06-20`\n"
            "• `/adddeadline Bài tập lớn 2025-06-25 CSDL`",
            parse_mode="Markdown",
        )
        return

    # Tìm arg nào là ngày (YYYY-MM-DD)
    date_idx = None
    for i, arg in enumerate(args):
        try:
            date.fromisoformat(arg)
            date_idx = i
            break
        except ValueError:
            continue

    if date_idx is None:
        await update.message.reply_text(
            "❌ Không tìm thấy ngày hợp lệ.\n"
            "Định dạng ngày: `YYYY-MM-DD` (vd: `2025-06-20`)",
            parse_mode="Markdown",
        )
        return

    title   = " ".join(args[:date_idx])
    due_str = args[date_idx]
    subject = " ".join(args[date_idx + 1:]) or None

    if not title:
        await update.message.reply_text("❌ Tiêu đề không được để trống.")
        return

    try:
        result = await api.add_deadline(tid, title, due_str, subject)
        days = _days_left(due_str)
        icon = _urgency_icon(days)
        await update.message.reply_text(
            f"✅ *Đã thêm deadline!*\n\n"
            f"{icon} *{title}*\n"
            f"📅 Hạn nộp: `{due_str}`"
            + (f"\n📚 Môn: {subject}" if subject else "")
            + (f"\n⏱ Còn {days} ngày" if days >= 0 else "\n⚠️ Đã qua hạn!"),
            parse_mode="Markdown",
        )
    except Exception as e:
        logger.error("adddeadline_handler: %s", e)
        await update.message.reply_text(f"❌ Lỗi thêm deadline: {e}")


async def donedl_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """/donedl <id> — Đánh dấu deadline đã hoàn thành."""
    tid = update.effective_user.id
    args = context.args or []
    if not args:
        await update.message.reply_text("Dùng: `/donedl <id>`", parse_mode="Markdown")
        return
    try:
        dl_id = int(args[0])
        await api.done_deadline(tid, dl_id)
        await update.message.reply_text(f"✅ Đã đánh dấu hoàn thành deadline #{dl_id}!")
    except Exception as e:
        await update.message.reply_text(f"❌ Lỗi: {e}")


async def deadline_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Xử lý InlineKeyboard của deadline."""
    query = update.callback_query
    await query.answer()
    tid = query.from_user.id

    if query.data == "dl_refresh":
        try:
            deadlines = await api.get_deadlines(tid)
            text = _format_deadline_list(deadlines)
            kb = InlineKeyboardMarkup([[
                InlineKeyboardButton("➕ Thêm deadline", callback_data="dl_add_hint"),
                InlineKeyboardButton("🔄 Làm mới",       callback_data="dl_refresh"),
            ]])
            await query.edit_message_text(text, parse_mode="Markdown", reply_markup=kb)
        except Exception as e:
            await query.edit_message_text(f"❌ Lỗi: {e}")

    elif query.data == "dl_add_hint":
        await query.edit_message_text(
            "📝 *Thêm deadline mới*\n\n"
            "`/adddeadline <tiêu đề> <YYYY-MM-DD> [môn học]`\n\n"
            "Ví dụ:\n"
            "• `/adddeadline Báo cáo Linux 2025-06-20`\n"
            "• `/adddeadline Bài tập lớn 2025-06-25 CSDL`",
            parse_mode="Markdown",
        )
