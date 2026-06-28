# ============================================================
#  Handler – Lịch sinh hoạt (Daily Schedule)
#  /syncdaily  — Đồng bộ lịch sinh hoạt từ Google Sheet
#  /daily      — Xem lịch sinh hoạt hôm nay (tích hợp TKB)
#  /dailyweek  — Xem lịch sinh hoạt cả tuần (tóm tắt)
# ============================================================

import logging
from datetime import datetime
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.error import BadRequest
from telegram.ext import ContextTypes

from services.api_client import api
from handlers.menu import MAIN_KEYBOARD

logger = logging.getLogger(__name__)

DOW_NAMES = {1: "Thứ 2", 2: "Thứ 3", 3: "Thứ 4", 4: "Thứ 5",
             5: "Thứ 6", 6: "Thứ 7", 7: "Chủ nhật"}

CAT_ICONS = {
    "Học tập":   "📚",
    "Nghỉ ngơi": "😴",
    "Sinh hoạt": "🍜",
    "Sức khỏe":  "💪",
    "Giải trí":  "🎮",
    "Khác":      "📌",
}


def _cat_icon(category: str) -> str:
    return CAT_ICONS.get(category, "📌")


def _merge_with_tkb(activities: list[dict], classes: list[dict]) -> list[dict]:
    """
    Ghép lịch sinh hoạt + TKB lớp thành 1 timeline thống nhất.
    TKB được convert sang cùng format activity rồi sắp xếp theo giờ bắt đầu.
    """
    merged = list(activities)

    for c in classes:
        subject = c.get("subjectName") or c.get("subject") or "?"
        room    = c.get("room") or ""
        teacher = c.get("teacher") or ""
        note_parts = [p for p in [room, teacher] if p]
        merged.append({
            "startTime": c.get("startTime", ""),
            "endTime":   c.get("endTime",   ""),
            "activity":  f"🏫 {subject}",
            "category":  "Học tập",
            "note":      " · ".join(note_parts) if note_parts else None,
            "_is_class": True,
        })

    # Sắp xếp theo giờ bắt đầu (HH:MM)
    merged.sort(key=lambda x: (x.get("startTime") or "")[:5])
    return merged


def _format_daily(activities: list[dict], day_name: str,
                  classes: list[dict] | None = None) -> str:
    """
    Format timeline ngày.
    Nếu có classes → ghép TKB vào; highlight giờ hiện tại.
    """
    if classes is not None:
        timeline = _merge_with_tkb(activities, classes)
    else:
        timeline = sorted(activities, key=lambda x: (x.get("startTime") or ""))

    if not timeline:
        curr_date = datetime.now().strftime("%d/%m/%Y")
        return (
            f"📅 *Lịch sinh hoạt {day_name}*\n\n"
            f"⚠️ Ngày {curr_date} chưa được cài đặt hoặc lỗi."
        )

    now_str = datetime.now().strftime("%H:%M")
    lines   = [f"📅 *Lịch sinh hoạt {day_name}*\n"]

    for act in timeline:
        start    = (act.get("startTime") or "")[:5]
        end      = (act.get("endTime")   or "")[:5]
        activity = act.get("activity", "?")
        category = act.get("category", "Khác")
        note     = act.get("note") or ""
        is_class = act.get("_is_class", False)

        # Highlight khung giờ hiện tại
        is_now = start <= now_str <= end if start and end else False
        prefix = "▶️" if is_now else ("🏫" if is_class else _cat_icon(category))

        # Nếu là class, activity đã có icon 🏫 prefix → dùng icon cat khác
        if is_class:
            prefix = "▶️" if is_now else "🏫"
            activity = activity.replace("🏫 ", "")   # bỏ icon trong tên

        note_line = f"\n    💬 _{note}_" if note else ""
        bold = "**" if is_now else ""
        lines.append(f"{prefix} `{start}–{end}` {activity}{note_line}")

    class_count = sum(1 for a in timeline if a.get("_is_class"))
    if class_count:
        lines.append(f"\n_🏫 {class_count} buổi học · 📌 {len(timeline)-class_count} hoạt động_")

    return "\n".join(lines)


async def daily_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """/daily — Xem lịch sinh hoạt hôm nay, tích hợp TKB lớp."""
    tid = update.effective_user.id
    try:
        java_dow = datetime.now().isoweekday()
        day_name = f"{DOW_NAMES.get(java_dow, 'Hôm nay')} ({datetime.now().strftime('%d/%m/%Y')})"

        # Tải song song: lịch sinh hoạt + TKB lớp hôm nay
        activities, classes = await _fetch_combined(tid, java_dow)

        text = _format_daily(activities, day_name, classes)
        kb = InlineKeyboardMarkup([[
            InlineKeyboardButton("📆 Cả tuần",  callback_data="daily_week"),
            InlineKeyboardButton("🔄 Làm mới",  callback_data="daily_today"),
            InlineKeyboardButton("🔗 Đồng bộ",  callback_data="daily_sync"),
        ]])
        await update.message.reply_text(text, parse_mode="Markdown", reply_markup=kb)
    except Exception as e:
        logger.error("daily_handler: %s", e)
        await update.message.reply_text(
            "❌ Lỗi tải lịch sinh hoạt.\n\n"
            "Thử lại: /syncdaily để đồng bộ từ Google Sheet.",
            reply_markup=MAIN_KEYBOARD,
        )


async def _fetch_combined(tid: int, java_dow: int) -> tuple[list, list]:
    """Tải đồng thời lịch sinh hoạt + TKB, trả về (activities, classes)."""
    import asyncio
    activities_task = asyncio.create_task(api.get_daily_schedule(tid, java_dow))
    classes_task    = asyncio.create_task(api.get_today_schedule(tid))

    results = await asyncio.gather(activities_task, classes_task, return_exceptions=True)

    activities = results[0] if not isinstance(results[0], Exception) else []
    classes    = results[1] if not isinstance(results[1], Exception) else []
    return activities, classes


async def syncdaily_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """/syncdaily — Đồng bộ lịch sinh hoạt từ Google Sheet."""
    tid = update.effective_user.id
    msg = await update.message.reply_text("🔄 Đang đồng bộ lịch sinh hoạt từ Google Sheet...")
    try:
        result = await api.sync_daily_sheet(tid)
        count  = result.get("syncedCount", 0)
        errors = result.get("errors", [])

        if result.get("success"):
            text = (
                f"✅ *Đồng bộ lịch sinh hoạt hoàn tất!*\n\n"
                f"📋 Đã sync *{count}* hoạt động\n"
            )
            if errors:
                text += f"⚠️ {len(errors)} lỗi nhỏ (bỏ qua)\n"
            text += "\nDùng /daily để xem lịch hôm nay!"
        else:
            text = f"❌ {result.get('message', 'Lỗi đồng bộ')}"

        await msg.edit_text(text, parse_mode="Markdown")
    except Exception as e:
        logger.error("syncdaily_handler: %s", e)
        await msg.edit_text(
            f"❌ Lỗi đồng bộ: {e}\n\n"
            "Đảm bảo đã cài Google Sheet bằng /setsheet"
        )


async def dailyweek_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """/dailyweek — Xem lịch sinh hoạt tóm tắt cả tuần."""
    tid = update.effective_user.id
    try:
        all_acts = await api.get_all_daily_schedule(tid)
        if not all_acts:
            await update.message.reply_text(
                "📅 Chưa có lịch sinh hoạt.\nDùng /syncdaily để đồng bộ.",
                reply_markup=MAIN_KEYBOARD,
            )
            return

        text = "📆 *Lịch sinh hoạt cả tuần*\n\n"

        all_day = [a for a in all_acts if not a.get("dayOfWeek")]
        if all_day:
            text += "*🔁 Lặp lại mỗi ngày:*\n"
            for act in all_day[:8]:
                start = (act.get("startTime") or "")[:5]
                end   = (act.get("endTime")   or "")[:5]
                icon  = _cat_icon(act.get("category", "Khác"))
                text += f"  {icon} `{start}–{end}` {act.get('activity','?')}\n"
            text += "\n"

        by_day: dict[int, list] = {}
        for act in all_acts:
            d = act.get("dayOfWeek")
            if d:
                by_day.setdefault(d, []).append(act)

        for d in sorted(by_day.keys()):
            day_acts = by_day[d]
            day_name = DOW_NAMES.get(d, f"Ngày {d}")
            text += f"*{day_name}*\n"
            for act in day_acts[:5]:
                start = (act.get("startTime") or "")[:5]
                icon  = _cat_icon(act.get("category", "Khác"))
                text += f"  {icon} `{start}` {act.get('activity','?')}\n"
            text += "\n"

        if len(text) > 4000:
            text = text[:3900] + "\n_(còn tiếp...)_"

        kb = InlineKeyboardMarkup([[
            InlineKeyboardButton("📅 Hôm nay", callback_data="daily_today"),
            InlineKeyboardButton("🔄 Đồng bộ", callback_data="daily_sync"),
        ]])
        await update.message.reply_text(text, parse_mode="Markdown", reply_markup=kb)

    except Exception as e:
        logger.error("dailyweek_handler: %s", e)
        await update.message.reply_text(f"❌ Lỗi: {e}")


async def daily_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Inline keyboard callbacks cho daily schedule."""
    query = update.callback_query
    await query.answer()
    tid  = query.from_user.id
    data = query.data

    if data == "daily_today":
        try:
            java_dow   = datetime.now().isoweekday()
            day_name   = f"{DOW_NAMES.get(java_dow, 'Hôm nay')} ({datetime.now().strftime('%d/%m/%Y')})"
            activities, classes = await _fetch_combined(tid, java_dow)
            text = _format_daily(activities, day_name, classes)
            kb = InlineKeyboardMarkup([[
                InlineKeyboardButton("📆 Cả tuần", callback_data="daily_week"),
                InlineKeyboardButton("🔄 Làm mới",  callback_data="daily_today"),
                InlineKeyboardButton("🔗 Đồng bộ",  callback_data="daily_sync"),
            ]])
            await query.edit_message_text(text, parse_mode="Markdown", reply_markup=kb)
        except BadRequest as e:
            if "Message is not modified" in str(e):
                await query.answer("Lịch học đã mới nhất!")
            else:
                await query.edit_message_text(f"❌ Lỗi: {e}")
        except Exception as e:
            await query.edit_message_text(f"❌ Lỗi: {e}")

    elif data == "daily_sync":
        await query.edit_message_text("🔄 Đang đồng bộ...")
        try:
            result = await api.sync_daily_sheet(tid)
            count  = result.get("syncedCount", 0)
            if result.get("success"):
                await query.edit_message_text(
                    f"✅ Đồng bộ xong! {count} hoạt động.\n"
                    "Dùng /daily để xem lịch hôm nay."
                )
            else:
                await query.edit_message_text(f"❌ {result.get('message','Lỗi')}")
        except Exception as e:
            await query.edit_message_text(f"❌ Lỗi: {e}")

    elif data == "daily_week":
        try:
            all_acts = await api.get_all_daily_schedule(tid)
            text = "📆 *Tóm tắt lịch sinh hoạt*\n\n"
            all_day = [a for a in all_acts if not a.get("dayOfWeek") and not a.get("date")]
            if all_day:
                text += "*🔁 Lặp lại mỗi ngày:*\n"
                for act in all_day[:6]:
                    start = (act.get("startTime") or "")[:5]
                    icon  = _cat_icon(act.get("category", "Khác"))
                    text += f"  {icon} `{start}` {act.get('activity','?')}\n"
                text += "\n"

            dated_acts = [a for a in all_acts if a.get("date")]
            recurring_acts = [a for a in all_acts if a.get("dayOfWeek") and not a.get("date")]

            if dated_acts:
                by_date = {}
                for a in dated_acts:
                    by_date.setdefault(a.get("date"), []).append(a)
                for d_str in sorted(by_date.keys()):
                    dt = datetime.strptime(d_str, "%Y-%m-%d")
                    day_name = DOW_NAMES.get(dt.isoweekday(), "Ngày khác")
                    date_formatted = dt.strftime("%d/%m/%Y")
                    text += f"*{day_name} ({date_formatted}):* {len(by_date[d_str])} hoạt động\n"

            if recurring_acts:
                by_dow = {}
                for a in recurring_acts:
                    by_dow.setdefault(a.get("dayOfWeek"), []).append(a)
                for dow in sorted(by_dow.keys()):
                    day_name = DOW_NAMES.get(dow, f"Thứ {dow}")
                    text += f"*{day_name} (Hàng tuần):* {len(by_dow[dow])} hoạt động\n"

            kb = InlineKeyboardMarkup([[
                InlineKeyboardButton("📅 Hôm nay", callback_data="daily_today"),
            ]])
            await query.edit_message_text(text, parse_mode="Markdown", reply_markup=kb)
        except Exception as e:
            await query.edit_message_text(f"❌ Lỗi: {e}")
