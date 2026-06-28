# ============================================================
#  Handler – Cài đặt thông báo lịch
#  Submenu trong ⚙️ Cài đặt → 🔔 Thông báo
# ============================================================

import logging
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes

from services.api_client import api

logger = logging.getLogger(__name__)


def _notify_menu(settings: dict) -> InlineKeyboardMarkup:
    """Tạo InlineKeyboard hiển thị trạng thái từng loại thông báo."""
    def toggle(key: str, label: str, cb_on: str, cb_off: str):
        on = settings.get(key, False)
        icon = "✅" if on else "❌"
        text = f"{icon} {label}"
        data = cb_off if on else cb_on    # bấm → đổi sang trạng thái ngược
        return InlineKeyboardButton(text, callback_data=data)

    return InlineKeyboardMarkup([
        [toggle("notifyDailySummary", "Tóm tắt sáng",      "notify_on_summary",  "notify_off_summary")],
        [toggle("notifyClassRemind",  "Nhắc buổi học",      "notify_on_class",    "notify_off_class")],
        [toggle("notifyDeadline",     "Nhắc deadline",      "notify_on_deadline", "notify_off_deadline")],
        [toggle("notifyExam",         "Nhắc lịch thi",      "notify_on_exam",     "notify_off_exam")],
        [toggle("notifyHustEvents",   "Tự động sự kiện HUST", "notify_on_hust",     "notify_off_hust")],
        [
            InlineKeyboardButton("🕐 Giờ tóm tắt sáng",  callback_data="notify_set_time"),
            InlineKeyboardButton("⏱ Nhắc trước (phút)",  callback_data="notify_set_before"),
        ],
    ])


def _format_settings(s: dict) -> str:
    def icon(v): return "✅" if v else "❌"
    time   = s.get("dailySummaryTime", "07:00")
    before = s.get("classRemindBefore", 30)
    dl_d   = s.get("deadlineRemindBefore", 1440) // 60
    ex_d   = s.get("examRemindBeforeDays", 2)
    return (
        "🔔 *Cài đặt thông báo*\n"
        "━━━━━━━━━━━━━━━━━━━━\n\n"
        f"{icon(s.get('notifyDailySummary'))} Tóm tắt sáng lúc `{time}`\n"
        f"{icon(s.get('notifyClassRemind'))} Nhắc buổi học trước `{before}` phút\n"
        f"{icon(s.get('notifyDeadline'))} Nhắc deadline trước `{dl_d}` tiếng\n"
        f"{icon(s.get('notifyExam'))} Nhắc lịch thi trước `{ex_d}` ngày\n"
        f"{icon(s.get('notifyHustEvents', True))} Tự động nhập sự kiện HUST CTSV mỗi sáng\n\n"
        "_Bấm nút để bật/tắt từng loại_"
    )


async def notify_settings_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """/notifysettings — Xem và cài đặt thông báo."""
    tid = update.effective_user.id
    try:
        s = await api.get_notification_settings(tid)
        await update.message.reply_text(
            _format_settings(s),
            parse_mode="Markdown",
            reply_markup=_notify_menu(s),
        )
    except Exception as e:
        await update.message.reply_text(f"❌ Lỗi: {e}")


async def notify_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Xử lý toggle bật/tắt thông báo."""
    query = update.callback_query
    await query.answer()
    tid  = query.from_user.id
    data = query.data

    # Map callback_data → field + value
    TOGGLE_MAP = {
        "notify_on_summary":  ("notifyDailySummary",  True),
        "notify_off_summary": ("notifyDailySummary",  False),
        "notify_on_class":    ("notifyClassRemind",   True),
        "notify_off_class":   ("notifyClassRemind",   False),
        "notify_on_deadline": ("notifyDeadline",      True),
        "notify_off_deadline":("notifyDeadline",      False),
        "notify_on_exam":     ("notifyExam",          True),
        "notify_off_exam":    ("notifyExam",          False),
        "notify_on_hust":     ("notifyHustEvents",    True),
        "notify_off_hust":    ("notifyHustEvents",    False),
    }

    if data in TOGGLE_MAP:
        field, value = TOGGLE_MAP[data]
        try:
            s = await api.update_notification_settings(tid, {field: value})
            await query.edit_message_text(
                _format_settings(s),
                parse_mode="Markdown",
                reply_markup=_notify_menu(s),
            )
        except Exception as e:
            await query.edit_message_text(f"❌ Lỗi: {e}")

    elif data == "notify_set_time":
        context.user_data["notify_input"] = "time"
        await query.edit_message_text(
            "🕐 *Cài giờ tóm tắt sáng*\n\n"
            "Gửi giờ muốn nhận tóm tắt, vd: `06:30`",
            parse_mode="Markdown",
        )

    elif data == "notify_set_before":
        context.user_data["notify_input"] = "before"
        await query.edit_message_text(
            "⏱ *Nhắc trước buổi học bao nhiêu phút?*\n\n"
            "Gửi số phút, vd: `30` hoặc `15`",
            parse_mode="Markdown",
        )


async def notify_input_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
    """
    Xử lý text input từ user khi đang trong chế độ cài đặt thông báo.
    Trả về True nếu đã xử lý, False nếu không phải input thông báo.
    """
    mode = context.user_data.get("notify_input")
    if not mode:
        return False

    tid  = update.effective_user.id
    text = update.message.text.strip()

    try:
        if mode == "time":
            # Validate HH:MM
            parts = text.split(":")
            if len(parts) != 2 or not all(p.isdigit() for p in parts):
                await update.message.reply_text("❌ Sai định dạng. Nhập kiểu `HH:MM` vd: `06:30`", parse_mode="Markdown")
                return True
            s = await api.update_notification_settings(tid, {"dailySummaryTime": text})
            context.user_data.pop("notify_input", None)
            await update.message.reply_text(
                f"✅ Đã cài giờ tóm tắt sáng: `{text}`\n\n" + _format_settings(s),
                parse_mode="Markdown",
                reply_markup=_notify_menu(s),
            )

        elif mode == "before":
            minutes = int(text)
            if minutes < 5 or minutes > 120:
                await update.message.reply_text("❌ Nhập từ 5 đến 120 phút.")
                return True
            s = await api.update_notification_settings(tid, {"classRemindBefore": minutes})
            context.user_data.pop("notify_input", None)
            await update.message.reply_text(
                f"✅ Sẽ nhắc trước buổi học `{minutes}` phút\n\n" + _format_settings(s),
                parse_mode="Markdown",
                reply_markup=_notify_menu(s),
            )
    except Exception as e:
        await update.message.reply_text(f"❌ Lỗi: {e}")
        context.user_data.pop("notify_input", None)

    return True
