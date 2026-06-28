# ============================================================
#  Handler – Sự kiện HUST CTSV
#  /hustsync   — Lấy sự kiện mới nhất từ ctsv.hust.edu.vn
#  /hustevents — Xem danh sách sự kiện đang/sắp diễn ra
# ============================================================

import logging
import httpx
from datetime import datetime

from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes

from services.api_client import api
from handlers.menu import MAIN_KEYBOARD

logger = logging.getLogger(__name__)

HUST_API = "https://ctsv.hust.edu.vn/api-t/Activity/GetPublishActivity"

TYPE_ICONS = {
    "Hội thảo hướng nghiệp":      "🎓",
    "Sinh hoạt chuyên đề":         "📖",
    "Hoạt động khảo sát":          "📋",
    "Giáo dục Chính trị & Tư tưởng": "📰",
    "Hoạt động thể thao":          "⚽",
    "Văn nghệ":                    "🎵",
    "Tình nguyện":                 "🤝",
    "Nghiên cứu khoa học":         "🔬",
    "Học bổng":                    "💰",
    "Tuyển dụng":                  "💼",
}


def _icon(atype: str) -> str:
    for key, icon in TYPE_ICONS.items():
        if key.lower() in (atype or "").lower():
            return icon
    return "📌"


def _parse_dt(s: str) -> datetime | None:
    if not s:
        return None
    for fmt in ["%Y-%m-%dT%H:%M:%S", "%Y-%m-%d %H:%M:%S", "%Y-%m-%dT%H:%M:%S.%f"]:
        try:
            return datetime.strptime(s[:19], fmt[:len(s[:19])])
        except ValueError:
            pass
    return None


async def _fetch_event_criteria(aid: int) -> list[dict]:
    """Lấy tiêu chí ĐRL của 1 sự kiện từ GetActivityById."""
    try:
        async with httpx.AsyncClient(timeout=8) as client:
            r = await client.post(
                f"{HUST_API.rsplit('/',1)[0]}/GetActivityById",
                json={"AId": aid},
                headers={"Content-Type": "application/json"},
            )
            if r.status_code == 200:
                acts = r.json().get("Activities", [])
                if acts:
                    return acts[0].get("CriteriaLst") or []
    except Exception:
        pass
    return []


async def _fetch_hust_events() -> dict:
    """Gọi API HUST CTSV và trả về events chia 2 nhóm: sắp + đang diễn ra."""
    async with httpx.AsyncClient(timeout=15) as client:
        r = await client.post(
            HUST_API,
            json={"NumberRow": 100, "PageNumber": 1},
            headers={"Content-Type": "application/json"},
        )
        r.raise_for_status()
        data = r.json()

    now = datetime.now()
    activities = data.get("Activities", [])

    upcoming, ongoing = [], []
    for a in activities:
        start  = _parse_dt(a.get("StartTime", ""))
        finish = _parse_dt(a.get("FinishTime", ""))
        if start is None:
            continue
        item = {
            "id":       a.get("AId"),
            "name":     a.get("AName", "?"),
            "type":     a.get("AType", ""),
            "place":    a.get("APlace", ""),
            "start":    start,
            "finish":   finish,
            "deadline": _parse_dt(a.get("Deadline", "")),
            "criteria": [],   # sẽ điền sau
        }
        if start > now:
            upcoming.append(item)
        elif finish and now <= finish:
            ongoing.append(item)

    upcoming.sort(key=lambda x: x["start"])
    ongoing.sort(key=lambda x: x["start"])

    # Lấy tiêu chí ĐRL cho sự kiện sắp tới (tối đa 10 đầu)
    import asyncio
    async def enrich(item):
        item["criteria"] = await _fetch_event_criteria(item["id"])
        return item

    if upcoming:
        enriched = await asyncio.gather(*[enrich(e) for e in upcoming[:10]])
        upcoming[:10] = enriched

    return {"upcoming": upcoming[:10], "ongoing": ongoing[:10]}


def _format_event(ev: dict, idx: int) -> str:
    icon     = _icon(ev["type"])
    name     = ev["name"]
    place    = ev["place"] or "?"
    atype    = ev["type"] or ""
    start    = ev["start"].strftime("%d/%m %H:%M") if ev["start"] else "?"
    finish   = ev["finish"].strftime("%d/%m") if ev["finish"] else "?"
    deadline = ev["deadline"].strftime("%d/%m %H:%M") if ev["deadline"] else None

    dl_line = f"  ⏳ Đăng ký trước: `{deadline}`\n" if deadline else ""

    # Tiêu chí ĐRL
    drl_line = ""
    criteria = ev.get("criteria", [])
    if criteria:
        parts = []
        for c in criteria:
            pts = c.get("CMaxPoint", 0)
            cname = c.get("CName", "")[:35]
            parts.append(f"⭐ `+{pts:.0f} đ` _{cname}_")
        drl_line = "  " + "\n  ".join(parts) + "\n"

    return (
        f"{icon} *{name}*\n"
        f"  📂 {atype}\n"
        f"  📍 {place}\n"
        f"  🕐 {start} → {finish}\n"
        f"{dl_line}"
        f"{drl_line}"
    )


async def hustevents_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """/hustevents — Xem sự kiện HUST CTSV đang/sắp diễn ra."""
    msg = await update.message.reply_text("🔄 Đang tải sự kiện từ HUST CTSV...")
    try:
        events = await _fetch_hust_events()
        upcoming = events["upcoming"]
        ongoing  = events["ongoing"]

        text = "🏫 *Sự kiện HUST CTSV*\n"
        text += f"_Cập nhật: {datetime.now().strftime('%d/%m %H:%M')}_\n\n"

        if upcoming:
            text += f"📅 *Sắp diễn ra ({len(upcoming)} sự kiện)*\n{'─'*24}\n"
            for i, ev in enumerate(upcoming[:5]):
                text += _format_event(ev, i) + "\n"

        if ongoing:
            text += f"\n⚡ *Đang diễn ra ({len(ongoing)} sự kiện)*\n{'─'*24}\n"
            for i, ev in enumerate(ongoing[:5]):
                text += _format_event(ev, i) + "\n"

        if not upcoming and not ongoing:
            text += "Hiện không có sự kiện nào.\n"

        kb = InlineKeyboardMarkup([
            [
                InlineKeyboardButton("🔄 Làm mới",         callback_data="hust_refresh"),
                InlineKeyboardButton("➕ Import deadline",  callback_data="hust_import_menu"),
            ],
            [
                InlineKeyboardButton("🌐 Xem trang CTSV",  url="https://ctsv.hust.edu.vn/#/danh-sach-su-kien"),
            ],
        ])

        if len(text) > 4096:
            text = text[:4000] + "\n_(còn tiếp, xem trang CTSV để xem đầy đủ)_"

        # Lưu vào context để dùng cho import
        context.user_data["hust_events"] = events

        await msg.edit_text(text, parse_mode="Markdown", reply_markup=kb)
    except Exception as e:
        logger.error("hustevents_handler: %s", e)
        await msg.edit_text(f"❌ Lỗi tải sự kiện HUST: {e}")


async def hust_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Callbacks cho sự kiện HUST."""
    query = update.callback_query
    await query.answer()
    tid  = query.from_user.id
    data = query.data

    if data == "hust_refresh":
        await query.edit_message_text("🔄 Đang tải lại...")
        try:
            events = await _fetch_hust_events()
            upcoming = events["upcoming"]
            ongoing  = events["ongoing"]
            context.user_data["hust_events"] = events

            text = "🏫 *Sự kiện HUST CTSV*\n"
            text += f"_Cập nhật: {datetime.now().strftime('%d/%m %H:%M')}_\n\n"

            if upcoming:
                text += f"📅 *Sắp diễn ra ({len(upcoming)})*\n"
                for ev in upcoming[:5]:
                    text += _format_event(ev, 0) + "\n"
            if ongoing:
                text += f"\n⚡ *Đang diễn ra ({len(ongoing)})*\n"
                for ev in ongoing[:5]:
                    text += _format_event(ev, 0) + "\n"
            if not upcoming and not ongoing:
                text += "Hiện không có sự kiện nào.\n"

            kb = InlineKeyboardMarkup([
                [
                    InlineKeyboardButton("🔄 Làm mới",        callback_data="hust_refresh"),
                    InlineKeyboardButton("➕ Import deadline", callback_data="hust_import_menu"),
                ],
                [InlineKeyboardButton("🌐 Xem trang CTSV", url="https://ctsv.hust.edu.vn/#/danh-sach-su-kien")],
            ])
            if len(text) > 4096:
                text = text[:4000] + "\n_(còn tiếp...)_"
            await query.edit_message_text(text, parse_mode="Markdown", reply_markup=kb)
        except Exception as e:
            await query.edit_message_text(f"❌ Lỗi: {e}")

    elif data == "hust_import_menu":
        events = context.user_data.get("hust_events", {})
        upcoming = events.get("upcoming", [])

        if not upcoming:
            await query.edit_message_text("Không có sự kiện sắp tới để import.")
            return

        buttons = []
        for ev in upcoming[:8]:
            start_str = ev["start"].strftime("%d/%m")
            label = f"{ev['name'][:25]}... ({start_str})" if len(ev["name"]) > 25 else f"{ev['name']} ({start_str})"
            buttons.append([InlineKeyboardButton(
                f"➕ {label}",
                callback_data=f"hust_import_{ev['id']}"
            )])
        buttons.append([InlineKeyboardButton("◀️ Quay lại", callback_data="hust_refresh")])

        await query.edit_message_text(
            "➕ *Import sự kiện vào Deadline*\n\nChọn sự kiện muốn thêm:",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup(buttons),
        )

    elif data.startswith("hust_import_"):
        event_id = int(data.replace("hust_import_", ""))
        events   = context.user_data.get("hust_events", {})
        all_evs  = events.get("upcoming", []) + events.get("ongoing", [])
        ev = next((e for e in all_evs if e["id"] == event_id), None)

        if not ev:
            await query.edit_message_text("❌ Không tìm thấy sự kiện.")
            return

        try:
            # Import vào deadline
            due_date = (ev.get("deadline") or ev["start"]).strftime("%Y-%m-%d")
            await api.add_deadline(
                telegram_id=tid,
                title=ev["name"],
                due_date=due_date,
                subject="HUST CTSV",
            )
            await query.edit_message_text(
                f"✅ *Đã thêm vào Deadline!*\n\n"
                f"📌 {ev['name']}\n"
                f"📅 Ngày: {due_date}\n\n"
                f"Xem bằng /deadline hoặc bấm 📆 Sự kiện",
                parse_mode="Markdown",
            )
        except Exception as e:
            await query.edit_message_text(f"❌ Lỗi import: {e}")
