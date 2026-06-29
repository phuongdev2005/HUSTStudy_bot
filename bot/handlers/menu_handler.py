# ============================================================
#  Menu Handler – Xử lý khi user bấm các nút keyboard
#
#  1. button_handler  – nhận text từ ReplyKeyboard (nút đáy)
#  2. menu_callback   – nhận callback từ InlineKeyboard (submenu)
# ============================================================

import asyncio
import logging
from datetime import datetime
from telegram import Update
from telegram.error import BadRequest
from telegram.ext import ContextTypes

from services.api_client import api

async def handle_callback_error(query, e: Exception, default_msg: str):
    if isinstance(e, BadRequest) and "Message is not modified" in str(e):
        await query.answer("Nội dung đã mới nhất!")
    else:
        logger.error(f"{default_msg}: {e}", exc_info=True)
        try:
            await query.edit_message_text(f"❌ Lỗi: {e}")
        except Exception:
            pass
from handlers.menu import (
    MAIN_KEYBOARD, BUTTON_TEXT_MAP,
    schedule_menu, expense_menu,
    events_menu, english_menu,
    settings_menu, report_menu,
)

logger = logging.getLogger(__name__)

DOW_NAMES = {1: "Thứ 2", 2: "Thứ 3", 3: "Thứ 4", 4: "Thứ 5",
             5: "Thứ 6", 6: "Thứ 7", 7: "Chủ nhật"}

CAT_ICONS = {
    "Học tập":   "📚", "Nghỉ ngơi": "😴",
    "Sinh hoạt": "🍜", "Sức khỏe":  "💪",
    "Giải trí":  "🎮", "Khác":      "📌",
}

_HELP_TEXT = (
    "❓ *Hướng dẫn HUSTStudy Bot*\n"
    "━━━━━━━━━━━━━━━━━━━━━━\n\n"
    "📅 *Lịch học*\n"
    "  TKB lớp + lịch sinh hoạt từ Google Sheet\n\n"
    "💸 *Chi tiêu*\n"
    "  • `/addexpense 35k cơm trưa`\n"
    "  • Gửi ảnh hóa đơn → AI scan tự động\n\n"
    "📚 *Học tập*\n"
    "  • `/deadline` — xem deadline\n"
    "  • `/adddeadline <tiêu đề> <YYYY-MM-DD>`\n"
    "  • `/exam` — lịch thi\n"
    "  • `/quiz` — ôn từ vựng\n"
    "  • `/addword apple - quả táo`\n\n"
    "⚙️ *Cài đặt*\n"
    "  • `/setsheet <link>` — Google Sheet\n"
    "  • `/setkey <groq_key>` — AI không giới hạn\n\n"
    "💡 Gửi ảnh bill để scan tự động!"
)


# ══════════════════════════════════════════════════════════════
#  1. ReplyKeyboard button handler
# ══════════════════════════════════════════════════════════════

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text   = update.message.text
    action = BUTTON_TEXT_MAP.get(text)
    if action is None:
        return

    tid = update.effective_user.id

    if action == "menu_schedule":
        await update.message.reply_text(
            "📅 *Lịch học*\nChọn chức năng (bạn có thể xem mẫu sheet [tại đây](https://docs.google.com/spreadsheets/d/1FEW6GRzRLXKhInkKIXzYr0473ioe2BDLjQAkNbBaco4/edit?usp=sharing)):",
            parse_mode="Markdown",
            reply_markup=schedule_menu(),
        )

    elif action == "menu_expense":
        await update.message.reply_text(
            "💸 *Chi tiêu*\n_Hoặc gửi ảnh hóa đơn để scan tự động_ 📷",
            parse_mode="Markdown",
            reply_markup=expense_menu(),
        )

    elif action == "menu_events":
        await update.message.reply_text(
            "📆 *Sự kiện*\nDeadline & Lịch thi:",
            parse_mode="Markdown",
            reply_markup=events_menu(),
        )

    elif action == "menu_english":
        await update.message.reply_text(
            "🇬🇧 *Học Tiếng Anh*\nÔn từ vựng & Quiz:",
            parse_mode="Markdown",
            reply_markup=english_menu(),
        )

    elif action == "menu_report":
        await update.message.reply_text(
            "📊 *Báo cáo*\nChọn loại:",
            parse_mode="Markdown",
            reply_markup=report_menu(),
        )

    elif action == "menu_settings":
        try:
            status = await api.get_key_status(tid)
            key_info = (
                "✅ Đang dùng Groq Key riêng"
                if status.get("hasOwnKey")
                else f"🤖 Quota AI: {status.get('usedToday',0)}/{status.get('freeLimit',10)} lượt hôm nay"
            )
        except Exception:
            key_info = "🤖 Quota AI: chưa xác định"

        await update.message.reply_text(
            f"⚙️ *Cài đặt*\n\n{key_info}\n\nChọn chức năng:",
            parse_mode="Markdown",
            reply_markup=settings_menu(),
        )

    elif action == "menu_help":
        await update.message.reply_text(
            _HELP_TEXT,
            parse_mode="Markdown",
            reply_markup=MAIN_KEYBOARD,
        )


# ══════════════════════════════════════════════════════════════
#  2. InlineKeyboard callback handler
# ══════════════════════════════════════════════════════════════

async def menu_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data
    tid  = query.from_user.id

    # ── SCHEDULE ─────────────────────────────────────────────
    if data == "schedule_today":
        await query.edit_message_text("⏳ Đang tải...")
        await _cb_schedule_today(query, tid)

    elif data == "schedule_week":
        await query.edit_message_text("⏳ Đang tải...")
        await _cb_schedule_week(query, tid)

    elif data == "schedule_daily_today":
        await query.edit_message_text("⏳ Đang tải lịch sinh hoạt...")
        await _cb_daily_today(query, tid)

    elif data == "schedule_daily_week":
        await query.edit_message_text("⏳ Đang tải...")
        await _cb_daily_week(query, tid)

    elif data == "schedule_sync":
        await query.edit_message_text("🔄 Đang đồng bộ TKB...")
        await _cb_sync_tkb(query, tid)

    elif data == "schedule_sync_daily":
        await query.edit_message_text("🔄 Đang đồng bộ lịch sinh hoạt...")
        await _cb_sync_daily(query, tid)

    elif data == "schedule_setsheet":
        context.user_data["waiting_setsheet"] = True
        await query.edit_message_text(
            "🔗 *Cài Google Sheet*\n\n"
            "Paste link Google Sheet của bạn vào đây:\n"
            "_(Sheet phải ở chế độ 'Anyone with link can view')_",
            parse_mode="Markdown",
        )

    # ── EXPENSE ──────────────────────────────────────────────
    elif data == "expense_add":
        context.user_data["waiting_expense_amount"] = "EXPENSE"
        await query.edit_message_text(
            "💸 *Ghi chi tiêu*\n\n"
            "Nhập số tiền bạn đã chi (hoặc `Số tiền | Ghi chú`):\n"
            "`35000`  •  `35k`  •  `35k | cơm trưa`",
            parse_mode="Markdown",
        )

    elif data == "expense_income":
        context.user_data["waiting_expense_amount"] = "INCOME"
        await query.edit_message_text(
            "💰 *Ghi thu nhập*\n\n"
            "Nhập số tiền bạn đã thu (hoặc `Số tiền | Ghi chú`):\n"
            "`500000`  •  `500k`  •  `500k | lương`",
            parse_mode="Markdown",
        )

    elif data == "expense_scan_hint":
        await query.edit_message_text(
            "📷 *Scan hóa đơn bằng AI*\n\n"
            "Chỉ cần *gửi ảnh hóa đơn/bill* vào chat!\n\n"
            "Bot tự động:\n"
            "1️⃣ Nhận diện số tiền & cửa hàng\n"
            "2️⃣ Phân loại danh mục\n"
            "3️⃣ Hiện preview để xác nhận\n\n"
            "🆓 Miễn phí 10 lần/ngày · `/setkey` để không giới hạn",
            parse_mode="Markdown",
        )

    elif data == "expense_manage_cat":
        await _cb_manage_categories(query, tid, context)

    elif data == "expense_add_cat":
        context.user_data["waiting_new_category"] = True
        await query.edit_message_text(
            "📂 *Thêm danh mục mới*\n\n"
            "Nhập tên danh mục (có thể kèm icon):\n"
            "`🏠 Nhà cửa`\n"
            "`☕ Cà phê`\n"
            "`💻 Công việc`",
            parse_mode="Markdown",
        )

    elif data in ("expense_report", "report_expense"):
        await query.edit_message_text("⏳ Đang tải báo cáo...")
        await _cb_report(query, tid)

    elif data in ("expense_history", "report_history"):
        await query.edit_message_text("⏳ Đang tải lịch sử...")
        await _cb_history(query, tid)

    elif data == "expense_export_excel":
        await _cb_export_excel_menu(query)

    elif data == "expense_export_confirm_month":
        await _cb_export_excel_execute(query, tid, context, "month")

    elif data == "expense_export_confirm_year":
        await _cb_export_excel_execute(query, tid, context, "year")

    elif data == "expense_export_confirm_all":
        await _cb_export_excel_execute(query, tid, context, "all")

    # ── EVENTS – Deadline ────────────────────────────────────
    elif data == "events_deadline":
        await query.edit_message_text("⏳ Đang tải deadline...")
        await _cb_deadline(query, tid)

    elif data == "events_add_deadline":
        await query.edit_message_text(
            "➕ *Thêm deadline*\n\n"
            "`/adddeadline <tiêu đề> <YYYY-MM-DD> [môn học]`\n\n"
            "• `/adddeadline Báo cáo Linux 2025-06-20`\n"
            "• `/adddeadline Bài tập lớn 2025-06-25 CSDL`",
            parse_mode="Markdown",
        )

    # ── EVENTS – Exam ─────────────────────────────────────────
    elif data == "events_exam":
        await query.edit_message_text("⏳ Đang tải lịch thi...")
        await _cb_exam(query, tid)

    elif data == "events_add_exam":
        await query.edit_message_text(
            "➕ *Thêm lịch thi*\n\n"
            "`/addexam <môn học> <YYYY-MM-DD> <HH:MM> [phòng]`\n\n"
            "• `/addexam Giải tích 1 2025-06-22 07:00`\n"
            "• `/addexam CSDL 2025-06-25 13:00 A305`",
            parse_mode="Markdown",
        )

    elif data == "events_hust":
        # Forward sang hustevents_handler
        from handlers.hust_events import hustevents_handler
        # Tạo fake update với message mới
        await query.edit_message_text("🔄 Đang tải sự kiện HUST CTSV...")
        from handlers.hust_events import _fetch_hust_events, _format_event, TYPE_ICONS, _icon
        from datetime import datetime as _dt
        try:
            events = await _fetch_hust_events()
            upcoming = events["upcoming"]
            ongoing  = events["ongoing"]
            context.user_data["hust_events"] = events

            text = "🏨 *Sự kiện HUST CTSV*\n"
            text += f"_Cập nhật: {_dt.now().strftime('%d/%m %H:%M')}_\n\n"

            if upcoming:
                text += f"📅 *Sắp diễn ra ({len(upcoming)})*\n" + "─"*20 + "\n"
                for ev in upcoming[:5]:
                    text += _format_event(ev, 0) + "\n"
            if ongoing:
                text += f"\n⚡ *Đang diễn ra ({len(ongoing)})*\n" + "─"*20 + "\n"
                for ev in ongoing[:5]:
                    text += _format_event(ev, 0) + "\n"
            if not upcoming and not ongoing:
                text += "Hiện không có sự kiện nào.\n"

            from telegram import InlineKeyboardMarkup, InlineKeyboardButton
            kb = InlineKeyboardMarkup([
                [
                    InlineKeyboardButton("🔄 Làm mới",         callback_data="hust_refresh"),
                    InlineKeyboardButton("➕ Import deadline",  callback_data="hust_import_menu"),
                ],
                [InlineKeyboardButton("🌐 Xem trang CTSV", url="https://ctsv.hust.edu.vn/#/danh-sach-su-kien")],
            ])
            if len(text) > 4096:
                text = text[:4000] + "\n_(còn tiếp...)_"
            await query.edit_message_text(text, parse_mode="Markdown", reply_markup=kb)
        except Exception as e:
            await query.edit_message_text(f"❌ Lỗi: {e}")

    # ── ENGLISH – Quiz ────────────────────────────────────────
    elif data == "english_quiz":
        await query.edit_message_text("🧠 Đang lấy từ cần ôn...")
        await _cb_quiz(query, tid, context)

    elif data == "english_add_word":
        await query.edit_message_text(
            "➕ *Thêm từ vựng*\n\n"
            "`/addword <từ tiếng Anh> - <nghĩa tiếng Việt>`\n\n"
            "• `/addword computer - máy tính`\n"
            "• `/addword algorithm - thuật toán`",
            parse_mode="Markdown",
        )

    elif data == "english_words":
        await query.edit_message_text("⏳ Đang tải danh sách từ...")
        await _cb_words(query, tid)

    # ── REPORT ───────────────────────────────────────────────
    elif data == "report_schedule":
        await query.edit_message_text("⏳ Đang tải...")
        await _cb_schedule_today(query, tid)

    elif data == "report_daily":
        await query.edit_message_text("⏳ Đang tải lịch sinh hoạt...")
        await _cb_daily_today(query, tid)

    elif data == "report_deadline":
        await query.edit_message_text("⏳ Đang tải deadline...")
        await _cb_deadline(query, tid)

    elif data == "report_exam":
        await query.edit_message_text("⏳ Đang tải lịch thi...")
        await _cb_exam(query, tid)

    # ── SETTINGS ─────────────────────────────────────────────
    elif data == "settings_setsheet":
        context.user_data["waiting_setsheet"] = True
        await query.edit_message_text(
            "🔗 *Cài Google Sheet*\n\n"
            "Paste link Google Sheet của bạn vào đây:\n"
            "_(Sheet phải ở chế độ 'Anyone with link can view')_",
            parse_mode="Markdown",
        )

    elif data == "settings_setkey":
        await query.edit_message_text(
            "🤖 *Cài Groq API Key riêng*\n\n"
            "Lấy key miễn phí: https://console.groq.com/keys\n\n"
            "`/setkey gsk_xxxxxxxxxxxx`\n\n"
            "✅ Dùng key riêng = scan không giới hạn!\n"
            "❌ Xóa key: `/setkey` không có tham số",
            parse_mode="Markdown",
        )

    elif data == "settings_keystatus":
        try:
            status = await api.get_key_status(tid)
            await query.edit_message_text(status.get("message", "Không có thông tin"))
        except Exception as e:
            await query.edit_message_text(f"❌ Lỗi: {e}")

    elif data == "settings_notify":
        from handlers.notify_settings import _format_settings, _notify_menu
        try:
            s = await api.get_notification_settings(tid)
            await query.edit_message_text(
                _format_settings(s),
                parse_mode="Markdown",
                reply_markup=_notify_menu(s),
            )
        except Exception as e:
            await query.edit_message_text(f"❌ Lỗi mở cài đặt thông báo: {e}")

    elif data == "settings_reset_expense_confirm":
        from telegram import InlineKeyboardMarkup, InlineKeyboardButton
        kb = InlineKeyboardMarkup([
            [
                InlineKeyboardButton("🗑️ Có, xóa hết", callback_data="settings_reset_expense_execute"),
                InlineKeyboardButton("❌ Hủy", callback_data="settings_reset_expense_cancel"),
            ]
        ])
        await query.edit_message_text(
            "⚠️ *XÁC NHẬN RESET CHI TIÊU*\n\n"
            "Bạn có chắc chắn muốn xóa *TOÀN BỘ* lịch sử giao dịch (thu nhập & chi tiêu) không?\n"
            "Hành động này *không thể hoàn tác*!",
            parse_mode="Markdown",
            reply_markup=kb,
        )

    elif data == "settings_reset_expense_execute":
        try:
            res = await api.reset_expenses(tid)
            msg = res.get("message") or "✅ Đã reset toàn bộ dữ liệu giao dịch chi tiêu."
            await query.edit_message_text(msg)
        except Exception as e:
            await query.edit_message_text(f"❌ Lỗi khi reset dữ liệu: {e}")

    elif data == "settings_reset_expense_cancel":
        try:
            status = await api.get_key_status(tid)
            key_info = (
                "✅ Đang dùng Groq Key riêng"
                if status.get("hasOwnKey")
                else f"🤖 Quota AI: {status.get('usedToday',0)}/{status.get('freeLimit',10)} lượt hôm nay"
            )
        except Exception:
            key_info = "🤖 Quota AI: chưa xác định"

        await query.edit_message_text(
            f"⚙️ *Cài đặt*\n\n{key_info}\n\nChọn chức năng:",
            parse_mode="Markdown",
            reply_markup=settings_menu(),
        )


# ══════════════════════════════════════════════════════════════
#  Private helpers
# ══════════════════════════════════════════════════════════════

def _fmt(amount) -> str:
    return f"{int(amount):,} đ".replace(",", ".")


async def _cb_schedule_today(query, tid: int):
    try:
        classes = await api.get_today_schedule(tid)
        if not classes:
            await query.edit_message_text("📅 Hôm nay không có lịch học! 🎉")
            return
        dow = ["T2","T3","T4","T5","T6","T7","CN"][datetime.now().weekday()]
        lines = [f"📅 *TKB hôm nay ({dow})*\n"]
        for c in classes:
            lines.append(
                f"🕐 {c.get('startTime','?')}–{c.get('endTime','?')}\n"
                f"  📖 {c.get('subjectName','?')}\n"
                f"  📍 {c.get('room','?')}  👤 {c.get('teacher','?')}\n"
            )
        await query.edit_message_text("\n".join(lines), parse_mode="Markdown")
    except Exception as e:
        await handle_callback_error(query, e, "Lỗi tải TKB")


async def _cb_schedule_week(query, tid: int):
    try:
        classes = await api.get_week_schedule(tid)
        if not classes:
            await query.edit_message_text("📆 Tuần này không có lịch học!")
            return
        days = {1:"Thứ 2",2:"Thứ 3",3:"Thứ 4",4:"Thứ 5",5:"Thứ 6",6:"Thứ 7",7:"CN"}
        grouped: dict = {}
        for c in classes:
            grouped.setdefault(c.get("dayOfWeek",0), []).append(c)
        lines = ["📆 *TKB cả tuần*\n"]
        for d in sorted(grouped):
            lines.append(f"*{days.get(d,f'Ngày {d}')}*")
            for c in grouped[d]:
                lines.append(f"  🕐 {c.get('startTime','?')} {c.get('subjectName','?')} – {c.get('room','?')}")
            lines.append("")
        text = "\n".join(lines)
        if len(text) > 4000:
            text = text[:3900] + "\n_(còn tiếp...)_"
        await query.edit_message_text(text, parse_mode="Markdown")
    except Exception as e:
        await handle_callback_error(query, e, "Lỗi tải TKB tuần")


async def _cb_sync_tkb(query, tid: int):
    try:
        r = await api.sync_sheet(tid)
        count = r.get("syncedCount", 0)
        await query.edit_message_text(
            f"✅ *Đồng bộ TKB xong!*\nĐã sync *{count}* môn học.",
            parse_mode="Markdown",
        )
    except Exception as e:
        await handle_callback_error(query, e, "Lỗi đồng bộ TKB")


async def _cb_sync_daily(query, tid: int):
    try:
        r = await api.sync_daily_sheet(tid)
        count = r.get("syncedCount", 0)
        if r.get("success"):
            await query.edit_message_text(
                f"✅ *Đồng bộ lịch sinh hoạt xong!*\nĐã sync *{count}* hoạt động.",
                parse_mode="Markdown",
            )
        else:
            await query.edit_message_text(f"❌ {r.get('message','Lỗi')}")
    except Exception as e:
        await handle_callback_error(query, e, "Lỗi đồng bộ lịch sinh hoạt")


async def _cb_daily_today(query, tid: int):
    try:
        java_dow = datetime.now().isoweekday()
        day_name = DOW_NAMES.get(java_dow, "Hôm nay")
        now_str  = datetime.now().strftime("%H:%M")

        # Tải song song lịch sinh hoạt + TKB
        acts_task    = asyncio.create_task(api.get_daily_schedule(tid, java_dow))
        classes_task = asyncio.create_task(api.get_today_schedule(tid))
        results = await asyncio.gather(acts_task, classes_task, return_exceptions=True)
        activities = results[0] if not isinstance(results[0], Exception) else []
        classes    = results[1] if not isinstance(results[1], Exception) else []

        # Ghép TKB vào timeline
        timeline = list(activities)
        for c in classes:
            subject = c.get("subjectName") or c.get("subject") or "?"
            room    = c.get("room") or ""
            teacher = c.get("teacher") or ""
            note_parts = [p for p in [room, teacher] if p]
            timeline.append({
                "startTime": c.get("startTime", ""),
                "endTime":   c.get("endTime",   ""),
                "activity":  subject,
                "category":  "Học tập",
                "note":      " · ".join(note_parts) if note_parts else None,
                "_is_class": True,
            })
        timeline.sort(key=lambda x: (x.get("startTime") or "")[:5])

        if not timeline:
            await query.edit_message_text(
                f"🌅 *Lịch sinh hoạt {day_name}*\n\nChưa có lịch.\nDùng /syncdaily để đồng bộ.",
                parse_mode="Markdown"
            )
            return

        lines = [f"🌅 *Lịch sinh hoạt {day_name}*\n"]
        for act in timeline:
            s        = (act.get("startTime") or "")[:5]
            e        = (act.get("endTime")   or "")[:5]
            activity = act.get("activity", "?")
            note     = act.get("note") or ""
            is_class = act.get("_is_class", False)
            is_now   = s <= now_str <= e if s and e else False
            icon     = "▶️" if is_now else ("🏫" if is_class else CAT_ICONS.get(act.get("category","Khác"),"📌"))
            note_line = f"\n    💬 _{note}_" if note else ""
            lines.append(f"{icon} `{s}–{e}` {activity}{note_line}")

        class_count = sum(1 for a in timeline if a.get("_is_class"))
        if class_count:
            lines.append(f"\n_🏫 {class_count} buổi học · 📌 {len(timeline)-class_count} hoạt động_")

        await query.edit_message_text("\n".join(lines), parse_mode="Markdown")
    except Exception as e:
        await handle_callback_error(query, e, "Lỗi tải lịch")


async def _cb_daily_week(query, tid: int):
    try:
        all_acts = await api.get_all_daily_schedule(tid)
        if not all_acts:
            await query.edit_message_text("🌅 Chưa có lịch sinh hoạt. Dùng /syncdaily")
            return
        lines = ["📆 *Lịch sinh hoạt cả tuần*\n"]

        # 1. Các hoạt động lặp lại hàng ngày (không có dayOfWeek và không có date)
        all_day = [a for a in all_acts if not a.get("dayOfWeek") and not a.get("date")]
        if all_day:
            lines.append("*🔁 Mỗi ngày:*")
            for a in all_day[:6]:
                s    = (a.get("startTime") or "")[:5]
                icon = CAT_ICONS.get(a.get("category","Khác"),"📌")
                lines.append(f"  {icon} `{s}` {a.get('activity','?')}")
            lines.append("")

        # 2. Phân loại theo ngày cụ thể (có date) vs thứ lặp lại (có dayOfWeek nhưng date là null)
        dated_acts = [a for a in all_acts if a.get("date")]
        recurring_acts = [a for a in all_acts if a.get("dayOfWeek") and not a.get("date")]

        if dated_acts:
            # Gom nhóm theo date (yyyy-MM-dd)
            by_date = {}
            for a in dated_acts:
                by_date.setdefault(a.get("date"), []).append(a)
            # Sắp xếp date tăng dần
            for d_str in sorted(by_date.keys()):
                dt = datetime.strptime(d_str, "%Y-%m-%d")
                day_name = DOW_NAMES.get(dt.isoweekday(), "Ngày khác")
                header_text = f"{day_name} ({dt.strftime('%d/%m/%Y')})"
                lines.append(f"*{header_text}*")
                for a in by_date[d_str][:6]:
                    s    = (a.get("startTime") or "")[:5]
                    icon = CAT_ICONS.get(a.get("category","Khác"),"📌")
                    lines.append(f"  {icon} `{s}` {a.get('activity','?')}")
                lines.append("")

        if recurring_acts:
            # Gom nhóm theo dayOfWeek (1..7)
            by_dow = {}
            for a in recurring_acts:
                by_dow.setdefault(a.get("dayOfWeek"), []).append(a)
            for dow in sorted(by_dow.keys()):
                day_name = DOW_NAMES.get(dow, f"Thứ {dow}")
                lines.append(f"*{day_name} (Hàng tuần)*")
                for a in by_dow[dow][:6]:
                    s    = (a.get("startTime") or "")[:5]
                    icon = CAT_ICONS.get(a.get("category","Khác"),"📌")
                    lines.append(f"  {icon} `{s}` {a.get('activity','?')}")
                lines.append("")

        text = "\n".join(lines)
        if len(text) > 4000:
            text = text[:3900] + "\n_(còn tiếp...)_"
        await query.edit_message_text(text, parse_mode="Markdown")
    except Exception as e:
        await handle_callback_error(query, e, "Lỗi tải lịch tuần")


async def _cb_deadline(query, tid: int):
    try:
        deadlines = await api.get_deadlines(tid)
        if not deadlines:
            await query.edit_message_text(
                "✅ Không có deadline nào!\n\n"
                "Thêm bằng: `/adddeadline <tiêu đề> <YYYY-MM-DD>`",
                parse_mode="Markdown",
            )
            return
        from datetime import date
        def days_left(s):
            try: return (date.fromisoformat(s) - date.today()).days
            except: return 999
        def icon(d):
            return "🔴" if d < 0 else "🆘" if d == 0 else "🔴" if d <= 2 else "🟡" if d <= 7 else "🟢"

        lines = ["⏰ *Deadline sắp tới*\n"]
        for dl in deadlines[:10]:
            if dl.get("isDone"): continue
            d    = days_left(dl.get("dueDate",""))
            ico  = icon(d)
            day_txt = "Quá hạn!" if d < 0 else "Hôm nay!" if d == 0 else f"Còn {d} ngày"
            subj = f"  📚 {dl.get('subject')}\n" if dl.get("subject") else ""
            lines.append(
                f"{ico} *{dl.get('title','?')}*\n"
                f"{subj}"
                f"  📅 {dl.get('dueDate','?')} · _{day_txt}_\n"
                f"  ✓ /donedl {dl.get('id','')}"
            )
        await query.edit_message_text("\n".join(lines), parse_mode="Markdown")
    except Exception as e:
        await query.edit_message_text(f"❌ Lỗi tải deadline: {e}")


async def _cb_exam(query, tid: int):
    try:
        exams = await api.get_exams(tid)
        if not exams:
            await query.edit_message_text(
                "🎉 Không có lịch thi nào sắp tới!\n\n"
                "Thêm bằng: `/addexam <môn> <YYYY-MM-DD> <HH:MM>`",
                parse_mode="Markdown",
            )
            return
        from datetime import date
        def days_left(s):
            try: return (date.fromisoformat(s) - date.today()).days
            except: return 999

        lines = ["📋 *Lịch thi sắp tới*\n"]
        for ex in exams[:8]:
            d   = days_left(ex.get("examDate",""))
            ico = "🆘" if d == 0 else "🔴" if d <= 3 else "🟡" if d <= 7 else "🟢"
            if d < 0: ico = "✅"
            day_txt = f"Còn {d} ngày" if d > 0 else "Hôm nay!" if d == 0 else f"Đã thi {abs(d)}N"
            time_str = (ex.get("startTime") or "")[:5]
            lines.append(
                f"{ico} *{ex.get('subject','?')}*\n"
                f"  📅 {ex.get('examDate','?')} 🕐 {time_str}\n"
                f"  📍 {ex.get('room') or 'Chưa có phòng'} · _{day_txt}_"
            )
        await query.edit_message_text("\n\n".join(lines), parse_mode="Markdown")
    except Exception as e:
        await query.edit_message_text(f"❌ Lỗi tải lịch thi: {e}")


async def _cb_quiz(query, tid: int, context):
    try:
        from telegram import InlineKeyboardMarkup, InlineKeyboardButton
        word = await api.get_next_quiz_word(tid)
        if not word:
            await query.edit_message_text(
                "📚 Chưa có từ vựng nào!\n\n"
                "Thêm từ: `/addword computer - máy tính`",
                parse_mode="Markdown",
            )
            return
        context.user_data["quiz_word"] = word
        word_id   = word.get("id")
        word_text = word.get("word","?")
        level     = word.get("level", 0)
        stars     = "⭐" * min(level,5) + "☆" * (5 - min(level,5))
        pron      = word.get("pronunciation") or ""
        kb = InlineKeyboardMarkup([
            [
                InlineKeyboardButton("✅ Biết rồi",    callback_data=f"quiz_know_{word_id}"),
                InlineKeyboardButton("❌ Chưa biết",   callback_data=f"quiz_dontknow_{word_id}"),
            ],
            [
                InlineKeyboardButton("👁 Xem đáp án",  callback_data=f"quiz_reveal_{word_id}"),
                InlineKeyboardButton("⏭ Bỏ qua",       callback_data=f"quiz_skip_{word_id}"),
            ],
        ])
        pron_line = f"\n🔊 {pron}" if pron else ""
        await query.edit_message_text(
            f"🧠 *Ôn từ vựng*\n\n"
            f"Từ: *{word_text}*{pron_line}\n"
            f"Level: {stars}\n\n"
            f"Nghĩa của từ này là gì?",
            parse_mode="Markdown",
            reply_markup=kb,
        )
    except Exception as e:
        await query.edit_message_text(f"❌ Lỗi: {e}")


async def _cb_words(query, tid: int):
    try:
        words = await api.get_all_words(tid)
        if not words:
            await query.edit_message_text(
                "📚 Chưa có từ vựng.\n\n"
                "Thêm: `/addword apple - quả táo`",
                parse_mode="Markdown",
            )
            return
        total = len(words)
        lines = [f"📚 *Từ vựng của bạn ({total} từ)*\n"]
        for w in words[:15]:
            stars = "⭐" * min(w.get("level",0), 5)
            lines.append(f"• *{w.get('word')}* — {w.get('meaning')} {stars}")
        if total > 15:
            lines.append(f"\n_... và {total-15} từ nữa. Dùng /words để xem hết_")
        await query.edit_message_text("\n".join(lines), parse_mode="Markdown")
    except Exception as e:
        await query.edit_message_text(f"❌ Lỗi: {e}")


async def _cb_report(query, tid: int):
    try:
        from handlers.expense import fmt_vnd
        report  = await api.get_expense_report(tid)
        history = await api.get_expense_history(tid, limit=5)

        te = report.get("totalExpense", 0)
        ti = report.get("totalIncome",  0)
        bl = ti - te
        categories = report.get("categories", [])

        cat_lines = ""
        if categories:
            for cat_stat in categories[:5]:
                cat_name = cat_stat.get("categoryName") or "Khác"
                cat_icon = cat_stat.get("categoryIcon") or ""
                amt = cat_stat.get("amount", 0)
                pct = int(amt / te * 10) if te > 0 else 0
                bar = "█" * pct + "░" * (10-pct)
                label = f"{cat_icon} {cat_name}".strip()
                cat_lines += f"\n  {label}: {fmt_vnd(amt)}\n  `{bar}`\n"

        recent = ""
        for tx in history[:5]:
            sign = "🔴" if tx.get("type") == "EXPENSE" else "🟢"
            recent += f"\n{sign} {fmt_vnd(tx.get('amount',0))}  {(tx.get('note') or tx.get('categoryName','—'))[:18]}"

        text = (
            f"📊 *Báo cáo tháng {report.get('month','')}/{report.get('year','')}*\n"
            f"{'─'*28}\n"
            f"💸 Chi: *{fmt_vnd(te)}*\n"
            f"💚 Thu: *{fmt_vnd(ti)}*\n"
            f"{'📈' if bl >= 0 else '📉'} Còn: *{fmt_vnd(abs(bl))}*"
            f"{'  ⚠️ âm!' if bl < 0 else ''}\n"
            f"\n📂 *Theo danh mục:*{cat_lines or ' Chưa có'}\n"
            f"\n🕐 *Gần đây:*{recent or ' Chưa có'}"
        )
        await query.edit_message_text(text, parse_mode="Markdown")
    except Exception as e:
        await query.edit_message_text(f"❌ Lỗi báo cáo: {e}")


async def _cb_history(query, tid: int):
    try:
        from handlers.expense import fmt_vnd
        history = await api.get_expense_history(tid, limit=10)
        if not history:
            await query.edit_message_text("📋 Chưa có giao dịch nào.")
            return
        lines = ["📋 *Lịch sử 10 giao dịch gần nhất*\n"]
        buttons = []
        from telegram import InlineKeyboardButton, InlineKeyboardMarkup
        for tx in history:
            sign = "🔴" if tx.get("type") == "EXPENSE" else "🟢"
            amt  = fmt_vnd(tx.get("amount",0))
            desc = (tx.get("note") or tx.get("categoryName") or "—")[:20]
            date = (tx.get("transactionAt") or tx.get("transactionDate") or "")[:10]
            tx_id = tx.get("id")
            lines.append(f"{sign} `{tx_id}` {amt}  {desc}  _{date}_")
            buttons.append([InlineKeyboardButton(f"🗑 Xóa #{tx_id}", callback_data=f"deleteexp_{tx_id}")])
        buttons.append([InlineKeyboardButton("◀️ Quay lại", callback_data="menu_expense")])
        await query.edit_message_text(
            "\n".join(lines),
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup(buttons)
        )
    except Exception as e:
        await query.edit_message_text(f"❌ Lỗi: {e}")


# ══════════════════════════════════════════════════════════════
#  Bắt text khi user nhập số tiền sau khi bấm nút menu
# ══════════════════════════════════════════════════════════════

async def expense_amount_input_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
    """
    Bắt text người dùng nhập khi bot đang chờ số tiền.
    Hỗ trợ nhập kèm ghi chú: "35k cơm trưa" -> Số tiền: 35000, Ghi chú: cơm trưa.
    """
    expense_type = context.user_data.get("waiting_expense_amount")
    if not expense_type:
        return False

    from handlers.expense import _parse_amount, _show_category_picker
    text = update.message.text.strip()

    # Tách từ đầu tiên để lấy số tiền, phần còn lại làm ghi chú
    parts = text.split(None, 1)
    amount = _parse_amount(parts[0])
    if not amount or amount <= 0:
        await update.message.reply_text(
            "❌ Số tiền không hợp lệ.\nNhập lại (VD: `35000`, `35k`, `35k | cơm trưa`):",
            parse_mode="Markdown"
        )
        return True  # Vẫn đang trong trạng thái chờ

    # Lấy ghi chú nếu có
    note = parts[1].strip() if len(parts) > 1 else None
    if note and note.startswith("|"):
        note = note[1:].strip()
    if not note:
        note = None

    # Xoá trạng thái chờ nhập tiền
    context.user_data.pop("waiting_expense_amount", None)

    # Lưu pending và hiện category picker
    context.user_data["pending_expense"] = {
        "amount": amount,
        "note":   note,
        "type":   expense_type,
    }
    await _show_category_picker(update, context, amount, note, expense_type=expense_type)
    return True


# ══════════════════════════════════════════════════════════════
#  Helper: Hiện danh sách danh mục để quản lý
# ══════════════════════════════════════════════════════════════

async def _cb_manage_categories(query, tid: int, context):
    """Hiện danh sách danh mục + nút sửa/xóa cho tất cả danh mục của user."""
    try:
        cats = await api.get_categories(tid)
        lines = ["⚙️ *Quản lý danh mục*\n"]
        buttons = []

        from telegram import InlineKeyboardButton, InlineKeyboardMarkup

        for cat in cats:
            icon   = cat.get("icon") or "📦"
            name   = cat.get("name", "")
            cat_id = cat.get("id")

            if name.lower() == "khác":
                buttons.append([
                    InlineKeyboardButton(f"{icon} {name}", callback_data=f"catdetail_{cat_id}")
                ])
                lines.append(f"📂 {icon} {name}")
                continue

            buttons.append([
                InlineKeyboardButton(f"{icon} {name}", callback_data=f"catdetail_{cat_id}"),
                InlineKeyboardButton("❌", callback_data=f"delcat_{cat_id}")
            ])
            lines.append(f"📂 {icon} {name}")

        buttons.append([
            InlineKeyboardButton("➕ Thêm danh mục mới", callback_data="expense_add_cat")
        ])
        buttons.append([
            InlineKeyboardButton("◀️ Quay lại", callback_data="expense_back")
        ])

        text = "\n".join(lines) + "\n\n• Bấm *Tên danh mục* để xem các giao dịch.\n• Trong từng danh mục có thể sửa/xóa giao dịch.\n• Bấm *❌* để xóa danh mục tự tạo."
        await query.edit_message_text(
            text,
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup(buttons)
        )
    except Exception as e:
        await query.edit_message_text(f"❌ Lỗi tải danh mục: {e}")


async def _cb_category_detail(query, tid: int, cat_id: int):
    """Show transactions inside one category with edit/delete actions."""
    try:
        from handlers.expense import fmt_vnd
        from telegram import InlineKeyboardButton, InlineKeyboardMarkup

        cats = await api.get_categories(tid)
        cat = next((c for c in cats if c.get("id") == cat_id), None)
        if not cat:
            await query.answer("Không tìm thấy danh mục", show_alert=True)
            return

        name = cat.get("name", "")
        icon = cat.get("icon") or "📦"
        history = await api.get_expense_history(tid, period="all", limit=10000)
        items = [tx for tx in history if (tx.get("categoryName") or "") == name]
        total = sum(float(tx.get("amount") or 0) for tx in items)

        lines = [
            f"📂 *{icon} {name}*",
            f"Tổng: *{fmt_vnd(total)}*",
            f"Số giao dịch: *{len(items)}*",
            "",
        ]
        buttons = []
        for tx in items[:20]:
            tx_id = tx.get("id")
            amount = fmt_vnd(tx.get("amount", 0))
            note = (tx.get("note") or "Không ghi chú")[:28]
            date = (tx.get("transactionAt") or tx.get("transactionDate") or "")[:10]
            lines.append(f"`#{tx_id}` {amount} - {note} _{date}_")
            buttons.append([
                InlineKeyboardButton(f"✏️ Sửa #{tx_id}", callback_data=f"editexp_{tx_id}"),
                InlineKeyboardButton(f"🗑 Xóa #{tx_id}", callback_data=f"deleteexp_cat_{cat_id}_{tx_id}"),
            ])

        if len(items) > 20:
            lines.append(f"\n... còn {len(items) - 20} giao dịch, xem đầy đủ trong lịch sử.")
        if not items:
            lines.append("Chưa có giao dịch nào trong danh mục này.")

        if name.lower() != "khác":
            buttons.append([
                InlineKeyboardButton("✏️ Sửa danh mục", callback_data=f"editcat_menu_{cat_id}")
            ])
        buttons.append([
            InlineKeyboardButton("◀️ Quay lại danh mục", callback_data="expense_manage_cat")
        ])
        await query.edit_message_text(
            "\n".join(lines),
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup(buttons)
        )
    except Exception as e:
        await query.edit_message_text(f"❌ Lỗi tải giao dịch danh mục: {e}")


async def _cb_edit_category_menu(query, tid: int, cat_id: int):
    """Mở menu sửa danh mục (đổi tên / đổi icon)."""
    try:
        cats = await api.get_categories(tid)
        cat = next((c for c in cats if c.get("id") == cat_id), None)
        if not cat:
            await query.answer("❌ Không tìm thấy danh mục", show_alert=True)
            return

        icon = cat.get("icon") or "📦"
        name = cat.get("name", "")

        from telegram import InlineKeyboardButton, InlineKeyboardMarkup
        kb = InlineKeyboardMarkup([
            [
                InlineKeyboardButton("📝 Đổi tên", callback_data=f"editcat_name_{cat_id}"),
                InlineKeyboardButton("🎨 Đổi Icon", callback_data=f"editcat_icon_{cat_id}"),
            ],
            [
                InlineKeyboardButton("◀️ Quay lại", callback_data="expense_manage_cat")
            ]
        ])

        await query.edit_message_text(
            f"✏️ *Chỉnh sửa danh mục*\n\n"
            f"• *Tên hiện tại:* {name}\n"
            f"• *Icon hiện tại:* {icon}\n\n"
            f"Chọn phần muốn chỉnh sửa:",
            parse_mode="Markdown",
            reply_markup=kb
        )
    except Exception as e:
        await query.edit_message_text(f"❌ Lỗi: {e}")


async def editcat_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Callback xử lý sự kiện sửa danh mục."""
    query = update.callback_query
    await query.answer()
    data = query.data
    tid = query.from_user.id

    parts = data.split("_")
    action = parts[1]  # "menu", "name", "icon"
    cat_id = int(parts[2])

    if action == "menu":
        await _cb_edit_category_menu(query, tid, cat_id)
    elif action == "name":
        context.user_data["waiting_edit_category_name"] = cat_id
        await query.edit_message_text(
            "📝 *Đổi tên danh mục*\n\n"
            "Nhập tên mới cho danh mục của bạn:\n"
            "_(Hoặc nhập /huy để hủy bỏ)_",
            parse_mode="Markdown"
        )
    elif action == "icon":
        context.user_data["waiting_edit_category_icon"] = cat_id
        await query.edit_message_text(
            "🎨 *Đổi Icon danh mục*\n\n"
            "Nhập emoji mới làm icon cho danh mục (chỉ nhập 1 emoji):\n"
            "_(Hoặc nhập /huy để hủy bỏ)_",
            parse_mode="Markdown"
        )


async def edit_category_name_input_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
    """Bắt tên mới khi user đổi tên danh mục."""
    cat_id = context.user_data.get("waiting_edit_category_name")
    if cat_id is None:
        return False

    text = update.message.text.strip()
    context.user_data.pop("waiting_edit_category_name", None)
    if not text or text == "/huy":
        await update.message.reply_text("❌ Đã hủy sửa tên danh mục.")
        return True

    tid = update.effective_user.id
    try:
        await api.update_category(tid, cat_id, name=text)
        await update.message.reply_text(f"✅ Đã đổi tên danh mục thành: *{text}*", parse_mode="Markdown")
    except Exception as e:
        await update.message.reply_text(f"❌ Lỗi sửa danh mục: {e}")
    return True


async def edit_category_icon_input_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
    """Bắt icon mới khi user đổi icon danh mục."""
    cat_id = context.user_data.get("waiting_edit_category_icon")
    if cat_id is None:
        return False

    text = update.message.text.strip()
    context.user_data.pop("waiting_edit_category_icon", None)
    if not text or text == "/huy":
        await update.message.reply_text("❌ Đã hủy sửa icon danh mục.")
        return True

    tid = update.effective_user.id
    try:
        # Lấy emoji đầu tiên đề phòng nhập nhiều kí tự
        icon = text[0] if text else "📦"
        await api.update_category(tid, cat_id, icon=icon)
        await update.message.reply_text(f"✅ Đã đổi icon danh mục thành: {icon}", parse_mode="Markdown")
    except Exception as e:
        await update.message.reply_text(f"❌ Lỗi sửa danh mục: {e}")
    return True


# ══════════════════════════════════════════════════════════════
#  Bắt text khi user nhập tên danh mục mới
# ══════════════════════════════════════════════════════════════

async def editexp_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Ask for new transaction values."""
    query = update.callback_query
    await query.answer()
    expense_id = int(query.data.split("_", 1)[1])
    context.user_data["waiting_edit_expense"] = expense_id
    await query.edit_message_text(
        "✏️ *Sửa giao dịch*\n\n"
        "Nhập theo một trong hai dạng:\n"
        "`50000 | Ăn sáng`\n"
        "`50000 | Đi chợ | Mua rau`\n\n"
        "Dạng 2 sẽ đổi cả danh mục. Nếu danh mục chưa có, backend sẽ đưa vào `Khác`.",
        parse_mode="Markdown"
    )


async def edit_expense_input_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
    """Handle text input for transaction editing."""
    expense_id = context.user_data.get("waiting_edit_expense")
    if expense_id is None:
        return False

    text = update.message.text.strip()
    if not text or text.startswith("/"):
        context.user_data.pop("waiting_edit_expense", None)
        await update.message.reply_text("Đã hủy sửa giao dịch.")
        return True

    parts = [p.strip() for p in text.split("|")]
    from handlers.expense import _parse_amount, fmt_vnd
    amount = _parse_amount(parts[0]) if parts else None
    if not amount or amount <= 0:
        await update.message.reply_text(
            "Số tiền không hợp lệ. Ví dụ: `50000 | Ăn sáng`",
            parse_mode="Markdown"
        )
        return True

    category_name = None
    note = None
    if len(parts) >= 3:
        category_name = parts[1] or None
        note = parts[2] or None
    elif len(parts) == 2:
        note = parts[1] or None

    context.user_data.pop("waiting_edit_expense", None)
    try:
        result = await api.update_expense(
            telegram_id=update.effective_user.id,
            expense_id=expense_id,
            amount=amount,
            category_name=category_name,
            note=note,
        )
        await update.message.reply_text(
            "✅ *Đã cập nhật giao dịch*\n\n"
            f"Số tiền: *{fmt_vnd(result.get('amount', amount))}*\n"
            f"Danh mục: {result.get('categoryIcon') or ''} {result.get('categoryName') or ''}\n"
            f"Ghi chú: {result.get('note') or '—'}",
            parse_mode="Markdown"
        )
    except Exception as e:
        await update.message.reply_text(f"❌ Lỗi sửa giao dịch: {e}")
    return True


async def new_category_input_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
    """Bắt tên danh mục mới sau khi user bấm 'Thêm danh mục mới'."""
    if not context.user_data.get("waiting_new_category"):
        return False

    text = update.message.text.strip()
    if not text or text.startswith("/"):
        context.user_data.pop("waiting_new_category", None)
        await update.message.reply_text("❌ Đã hủy thêm danh mục.")
        return True

    tid = update.effective_user.id

    # Tách icon (emoji) ra nếu có ở đầu
    parts = text.split(None, 1)
    if len(parts) == 2 and len(parts[0]) <= 4 and not any(c.isalpha() for c in parts[0]):
        icon, name = parts[0], parts[1]
    else:
        icon, name = "📂", text

    context.user_data.pop("waiting_new_category", None)
    try:
        result = await api.add_category(tid, name, icon=icon)
        await update.message.reply_text(
            f"✅ *Đã thêm danh mục!*\n\n"
            f"{icon} *{name}*\n\n"
            f"_Danh mục mới sẽ xuất hiện khi bạn ghi chi tiêu_",
            parse_mode="Markdown"
        )
    except Exception as e:
        await update.message.reply_text(f"❌ Lỗi thêm danh mục: {e}")
    return True


# ══════════════════════════════════════════════════════════════
#  Bắt text khi user paste link Google Sheet
# ══════════════════════════════════════════════════════════════

async def setsheet_input_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
    """Bat link Google Sheet sau khi user bam nut Cai Google Sheet."""
    if not context.user_data.get("waiting_setsheet"):
        return False

    text = update.message.text.strip()

    # Neu khong phai link sheets -> huy
    if text.startswith("/") or "docs.google.com/spreadsheets" not in text:
        context.user_data.pop("waiting_setsheet", None)
        await update.message.reply_text(
            "Link không hợp lệ hoặc đã hủy.\n"
            "Link phải có dạng: https://docs.google.com/spreadsheets/d/..."
        )
        return True

    context.user_data.pop("waiting_setsheet", None)
    tid = update.effective_user.id

    try:
        # Buoc 1: Luu link
        await api.set_sheet(tid, text)

        # Buoc 2: Thong bao dang sync
        msg = await update.message.reply_text(
            "Đã lưu link. Đang đồng bộ thời khóa biểu..."
        )

        # Buoc 3: Tu dong sync ngay
        try:
            sync  = await api.sync_sheet(tid)
            count = sync.get("syncedCount", 0)
            errs  = sync.get("errors", [])
            warn  = f"\n⚠️ {len(errs)} lỗi nhỏ." if errs else ""

            await msg.edit_text(
                f"Đã liên kết Google Sheet thành công!\n\n"
                f"📋 Đồng bộ được *{count}* môn học.{warn}\n\n"
                f"Dùng *Lịch hôm nay* để xem thời khóa biểu.",
                parse_mode="Markdown"
            )
        except Exception as sync_err:
            await msg.edit_text(
                f"Đã lưu Google Sheet!\n\n"
                f"❌ Đồng bộ tự động thất bại: {sync_err}\n\n"
                f"Bấm *Đồng bộ TKB* để thử lại.",
                parse_mode="Markdown"
            )

    except Exception as e:
        await update.message.reply_text(f"Loi luu sheet: {e}")

    return True


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


async def _cb_export_excel_menu(query):
    """Hiện menu lựa chọn khoảng thời gian xuất Excel."""
    from telegram import InlineKeyboardButton, InlineKeyboardMarkup
    kb = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("📅 Tháng này", callback_data="expense_export_confirm_month"),
            InlineKeyboardButton("📅 Năm này", callback_data="expense_export_confirm_year"),
        ],
        [
            InlineKeyboardButton("📅 Tất cả lịch sử", callback_data="expense_export_confirm_all"),
        ],
        [
            InlineKeyboardButton("◀️ Quay lại", callback_data="menu_expense")
        ]
    ])
    await query.edit_message_text(
        "📥 *Xuất dữ liệu chi tiêu ra Excel*\n\n"
        "Vui lòng chọn khoảng thời gian bạn muốn xuất báo cáo:",
        parse_mode="Markdown",
        reply_markup=kb
    )


async def _cb_export_excel_execute(query, tid: int, context, period: str):
    """Xuất file Excel (dạng CSV UTF-8 BOM) và gửi cho user."""
    from telegram import InlineKeyboardButton, InlineKeyboardMarkup
    period_labels = {"month": "tháng này", "year": "năm này", "all": "tất cả lịch sử"}
    label = period_labels.get(period, "tháng này")
    await query.edit_message_text(f"⏳ Đang thu thập dữ liệu chi tiêu {label} để xuất file...")

    try:
        # Lấy lịch sử tối đa 10000 dòng để export
        history = await api.get_expense_history(tid, period=period, limit=10000)
        if not history:
            await query.edit_message_text(
                f"⚠️ Không tìm thấy giao dịch nào trong khoảng thời gian {label}!",
                reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton("◀️ Quay lại", callback_data="expense_export_excel")
                ]])
            )
            return

        import csv
        import io
        from datetime import datetime

        # Tạo file CSV trong bộ nhớ
        output = io.StringIO()
        # Ghi UTF-8 BOM để Excel hiển thị tiếng Việt chuẩn xác
        output.write('\ufeff')

        writer = csv.writer(output, delimiter=',', lineterminator='\n')
        # Ghi tiêu đề cột
        writer.writerow(["Mã GD", "Thời gian", "Loại", "Số tiền (đ)", "Danh mục", "Ghi chú", "Nguồn"])

        for exp in history:
            t_str = exp.get("transactionAt", "")
            if t_str:
                try:
                    dt = datetime.fromisoformat(t_str.replace("Z", "+00:00"))
                    t_str = dt.strftime("%d/%m/%Y %H:%M:%S")
                except Exception:
                    pass

            g_type = "Chi tiêu" if exp.get("type") == "EXPENSE" else "Thu nhập"
            amount = int(exp.get("amount", 0))
            cat = f"{exp.get('categoryIcon','') or '📂'} {exp.get('categoryName','')}".strip()
            note = exp.get("note") or ""
            source = "AI Scan" if exp.get("source") == "AI_SCAN" else "Nhập tay"

            writer.writerow([exp.get("id"), t_str, g_type, amount, cat, note, source])

        csv_data = output.getvalue().encode('utf-8')
        file_bytes = io.BytesIO(csv_data)

        # Đặt tên file
        now_str = datetime.now().strftime('%Y%m%d_%H%M%S')
        file_bytes.name = f"Chi_tieu_{period}_{now_str}.csv"

        # Gửi file thông qua telegram bot
        await context.bot.send_document(
            chat_id=query.message.chat_id,
            document=file_bytes,
            filename=file_bytes.name,
            caption=f"📊 Báo cáo lịch sử chi tiêu của bạn ({label}).\n"
                    f"💡 *Mẹo:* File định dạng CSV mã hóa UTF-8 BOM, click đúp để mở trực tiếp trên Excel mà không bị lỗi font tiếng Việt."
        )

        # Cập nhật trạng thái tin nhắn cũ thành công
        await query.edit_message_text(
            f"✅ Đã xuất và gửi báo cáo chi tiêu {label} thành công!",
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("◀️ Quay lại", callback_data="menu_expense")
            ]])
        )

    except Exception as e:
        logger.error(f"Excel export error: {e}", exc_info=True)
        await query.edit_message_text(
            f"❌ Có lỗi xảy ra trong quá trình xuất Excel: {e}",
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("◀️ Quay lại", callback_data="expense_export_excel")
            ]])
        )


async def quick_expense_input_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
    """
    Xử lý ghi chi tiêu nhanh theo cú pháp:
    Số tiền | Danh mục | Cụ thể là tiền gì mua gì
    Ví dụ:
    50000 | Ăn uống | Mua bánh mì
    """
    text = update.message.text.strip()
    if "|" not in text:
        return False

    parts = [p.strip() for p in text.split("|")]
    if len(parts) < 2:
        return False

    from handlers.expense import _parse_amount, fmt_vnd
    amount = _parse_amount(parts[0])
    if amount is None or amount <= 0:
        return False

    cat_name = parts[1] if parts[1] else "Khác"
    note = parts[2] if (len(parts) > 2 and parts[2]) else None
    tid = update.effective_user.id

    try:
        await api.add_expense(
            telegram_id=tid,
            type_="EXPENSE",
            amount=amount,
            category_name=cat_name,
            note=note,
        )
        await update.message.reply_text(
            f"✅ *Đã ghi chi tiêu nhanh!*\n\n"
            f"🔴 Số tiền: *{fmt_vnd(amount)}*\n"
            f"📂 Danh mục: {cat_name}\n"
            f"📝 Ghi chú: {note or '—'}\n\n"
            f"_Dùng /report để xem tổng tháng này_",
            parse_mode="Markdown"
        )
    except Exception as e:
        logger.error("quick_expense error: %s", e)
        await update.message.reply_text(f"❌ Lỗi ghi chi tiêu nhanh: {e}")

    return True
