# ============================================================
#  Handler – Quản lý chi tiêu cá nhân
#
#  Lệnh:
#    /addexpense <số_tiền> [ghi chú]  – ghi chi tiêu tay
#    /addincome  <số_tiền> [ghi chú]  – ghi thu nhập tay
#    /report                           – báo cáo tháng này
#    /setkey <groq_key>                – cài API key riêng
#    /setkey                           – xóa API key riêng
#    /keystatus                        – xem quota AI hôm nay
#
#  Scan ảnh:  gửi ảnh bất kỳ → bot tự nhận diện bill
# ============================================================

import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

from services.api_client import api
from services.groq_vision import scan_bill_image

logger = logging.getLogger(__name__)


def fmt_vnd(amount: int | float) -> str:
    """Định dạng số tiền VND: 1447000 → 1.447.000 đ"""
    return f"{int(amount):,} đ".replace(",", ".")


# ══════════════════════════════════════════════════════════════
#  Helper
# ══════════════════════════════════════════════════════════════

def _parse_amount(text: str) -> int | None:
    """Parse '35000', '35k', '35K', '1.5tr', '1tr5' → số nguyên VND"""
    text = text.strip().lower().replace(",", "").replace(".", "")
    try:
        if text.endswith("tr"):
            return int(float(text[:-2]) * 1_000_000)
        if text.endswith("k"):
            return int(text[:-1]) * 1_000
        return int(text)
    except ValueError:
        return None


async def _require_registered(update: Update) -> bool:
    """Kiểm tra user đã /start chưa. Nếu chưa thì nhắc."""
    tid = update.effective_user.id
    if not await api.user_exists(tid):
        await update.message.reply_text(
            "⚠️ Bạn chưa đăng ký!\nDùng /start để bắt đầu."
        )
        return False
    return True


# ══════════════════════════════════════════════════════════════
#  /addexpense  <số_tiền> [ghi chú]
# ══════════════════════════════════════════════════════════════

async def addexpense_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Ghi chi tiêu nhập tay."""
    if not await _require_registered(update):
        return

    args = context.args
    if not args:
        await update.message.reply_text(
            "💸 *Cách dùng:*\n"
            "`/addexpense <số_tiền> [ghi chú]`\n\n"
            "Ví dụ:\n"
            "`/addexpense 35000 cơm trưa`\n"
            "`/addexpense 15k trà sữa`\n"
            "`/addexpense 1tr5 học phí`",
            parse_mode="Markdown"
        )
        return

    amount = _parse_amount(args[0])
    if not amount or amount <= 0:
        await update.message.reply_text("❌ Số tiền không hợp lệ.\nVí dụ: `35000`, `35k`, `1tr5`",
                                        parse_mode="Markdown")
        return

    note = " ".join(args[1:]) if len(args) > 1 else None

    # Lưu tạm vào context, chờ user chọn danh mục
    context.user_data["pending_expense"] = {
        "amount": amount,
        "note":   note,
        "type":   "EXPENSE",
    }

    await _show_category_picker(update, context, amount, note, expense_type="EXPENSE")


# ══════════════════════════════════════════════════════════════
#  /addincome  <số_tiền> [ghi chú]
# ══════════════════════════════════════════════════════════════

async def addincome_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Ghi thu nhập nhập tay."""
    if not await _require_registered(update):
        return

    args = context.args
    if not args:
        await update.message.reply_text(
            "💰 *Cách dùng:*\n"
            "`/addincome <số_tiền> [ghi chú]`\n\n"
            "Ví dụ:\n"
            "`/addincome 500000 học bổng`\n"
            "`/addincome 2tr làm thêm cuối tuần`",
            parse_mode="Markdown"
        )
        return

    amount = _parse_amount(args[0])
    if not amount or amount <= 0:
        await update.message.reply_text("❌ Số tiền không hợp lệ.", parse_mode="Markdown")
        return

    note = " ".join(args[1:]) if len(args) > 1 else None

    # Lưu tạm vào context, chờ user chọn danh mục thu nhập
    context.user_data["pending_expense"] = {
        "amount": amount,
        "note":   note,
        "type":   "INCOME",
    }

    await _show_category_picker(update, context, amount, note, expense_type="INCOME")


# ══════════════════════════════════════════════════════════════
#  /report  – Báo cáo tháng này
# ══════════════════════════════════════════════════════════════

async def report_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Xem báo cáo chi tiêu tháng này."""
    if not await _require_registered(update):
        return

    msg = await update.message.reply_text("⏳ Đang tổng hợp báo cáo...")

    try:
        report = await api.get_expense_report(update.effective_user.id)
        history = await api.get_expense_history(update.effective_user.id, limit=5)

        total_expense = report.get("totalExpense", 0)
        total_income  = report.get("totalIncome", 0)
        balance       = total_income - total_expense
        by_category   = report.get("byCategory", {})

        # Build category breakdown
        cat_lines = ""
        if by_category:
            sorted_cats = sorted(by_category.items(), key=lambda x: x[1], reverse=True)
            for cat, amt in sorted_cats[:6]:
                bar_pct = int(amt / total_expense * 10) if total_expense > 0 else 0
                bar = "█" * bar_pct + "░" * (10 - bar_pct)
                cat_lines += f"\n  {cat}: {fmt_vnd(amt)}\n  `{bar}`\n"

        # Recent transactions
        recent = ""
        for tx in history[:5]:
            sign  = "🔴" if tx.get("type") == "EXPENSE" else "🟢"
            amt   = fmt_vnd(tx.get("amount", 0))
            desc  = tx.get("note") or tx.get("categoryName") or "—"
            recent += f"\n{sign} {amt}  {desc[:20]}"

        balance_icon = "📈" if balance >= 0 else "📉"

        text = (
            f"📊 *Báo cáo tháng {report.get('month', '')}/{report.get('year', '')}*\n"
            f"{'─' * 30}\n"
            f"💸 Chi tiêu: *{fmt_vnd(total_expense)}*\n"
            f"💚 Thu nhập: *{fmt_vnd(total_income)}*\n"
            f"{balance_icon} Còn lại: *{fmt_vnd(abs(balance))}* {'(âm ⚠️)' if balance < 0 else ''}\n"
            f"\n📂 *Chi tiêu theo danh mục:*{cat_lines or ' Chưa có dữ liệu'}\n"
            f"\n🕐 *Giao dịch gần đây:*{recent or ' Chưa có dữ liệu'}"
        )

        await msg.edit_text(text, parse_mode="Markdown")

    except Exception as e:
        logger.error("report error: %s", e)
        await msg.edit_text("❌ Lỗi tải báo cáo. Thử lại sau!")


# ══════════════════════════════════════════════════════════════
#  Scan ảnh hóa đơn  (MessageHandler — ảnh gửi vào bot)
# ══════════════════════════════════════════════════════════════

async def photo_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Nhận ảnh từ user → gửi Groq Vision → hiện preview → user confirm.
    """
    if not await _require_registered(update):
        return

    tid = update.effective_user.id
    msg = await update.message.reply_text("🔍 Đang nhận diện hóa đơn...")

    try:
        # Lấy ảnh lớn nhất từ Telegram
        photo    = update.message.photo[-1]
        file_id  = photo.file_id
        tg_file  = await context.bot.get_file(file_id)
        img_data = await tg_file.download_as_bytearray()

        # Kiểm tra key status để lấy api_key nếu user có key riêng
        try:
            key_status  = await api.get_key_status(tid)
            user_key    = key_status.get("apiKey") or None
            remaining   = key_status.get("remaining", 10)
            has_own_key = key_status.get("hasOwnKey", False)
        except Exception:
            key_status  = {}
            user_key    = None
            remaining   = 10
            has_own_key = False

        # Nếu không có key riêng và hết quota free → chặn scan
        if not has_own_key and remaining <= 0:
            await msg.edit_text(
                "🚫 *Bạn đã dùng hết 10 lượt scan AI miễn phí hôm nay!*\n\n"
                "💡 Để dùng không giới hạn, lấy API key miễn phí tại:\n"
                "   https://console.groq.com/keys\n"
                "Sau đó cài vào bot: `/setkey <your_key>`",
                parse_mode="Markdown"
            )
            return

        # Lấy danh sách danh mục của user để gửi kèm vào prompt cho AI
        try:
            user_categories = await api.get_categories(tid)
            cat_names = [c.get("name") for c in user_categories if c.get("name")]
        except Exception:
            cat_names = []

        # Gọi Groq Vision (dùng key của user nếu có, fallback về owner key)
        result = await scan_bill_image(bytes(img_data), categories=cat_names, api_key=user_key)

        if not result.get("success"):
            err = result.get("error", "Không nhận diện được.")
            await msg.edit_text(f"❌ {err}")
            return

        amount      = result.get("amount", 0)
        description = result.get("description", "Không rõ")
        category    = result.get("category", "Khác")
        merchant    = result.get("merchant") or "Không rõ"
        confidence  = result.get("confidence", 0)
        conf_pct    = int(confidence * 100)

        # Lưu vào context để dùng khi confirm
        context.user_data["pending_scan"] = {
            "amount":       amount,
            "description":  description,
            "category":     category,
            "merchant":     merchant,
            "confidence":   confidence,
            "image_file_id": file_id,
        }

        # Hiện preview với nút confirm/cancel
        keyboard = InlineKeyboardMarkup([
            [
                InlineKeyboardButton("✅ Xác nhận lưu", callback_data="scan_confirm"),
                InlineKeyboardButton("✏️ Sửa số tiền",  callback_data="scan_edit"),
            ],
            [InlineKeyboardButton("❌ Hủy",            callback_data="scan_cancel")],
        ])

        conf_bar = "🟩" * (conf_pct // 10) + "⬜" * (10 - conf_pct // 10)

        await msg.edit_text(
            f"🧾 *Kết quả nhận diện hóa đơn*\n"
            f"{'─' * 30}\n"
            f"💰 Số tiền:   *{fmt_vnd(amount)}*\n"
            f"📂 Danh mục: {category}\n"
            f"🏪 Cửa hàng: {merchant}\n"
            f"📝 Mô tả:     {description}\n\n"
            f"🤖 Độ tin cậy: {conf_bar} {conf_pct}%\n\n"
            f"_Kiểm tra lại thông tin và xác nhận lưu_",
            parse_mode="Markdown",
            reply_markup=keyboard
        )

    except Exception as e:
        logger.error("photo_handler error: %s", e)
        await msg.edit_text("❌ Lỗi xử lý ảnh. Thử lại sau!")


# ══════════════════════════════════════════════════════════════
#  Callback xử lý nút Confirm / Edit / Cancel
# ══════════════════════════════════════════════════════════════

async def scan_callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Xử lý InlineKeyboard sau khi scan."""
    query    = update.callback_query
    await query.answer()

    tid      = query.from_user.id
    data     = query.data
    pending  = context.user_data.get("pending_scan")

    if not pending:
        await query.edit_message_text("⚠️ Phiên scan đã hết hạn. Gửi lại ảnh để scan.")
        return

    if data == "scan_cancel":
        context.user_data.pop("pending_scan", None)
        await query.edit_message_text("❌ Đã hủy. Không lưu giao dịch.")
        return

    if data == "scan_edit":
        await query.edit_message_text(
            f"✏️ *Sửa số tiền*\n\n"
            f"Số tiền AI nhận diện: *{fmt_vnd(pending['amount'])}*\n\n"
            f"Gửi số tiền đúng (VD: `45000` hoặc `45k`)\n"
            f"hoặc /cancel để hủy:",
            parse_mode="Markdown"
        )
        context.user_data["waiting_edit_amount"] = True
        return

    if data == "scan_confirm":
        try:
            result = await api.confirm_scan(
                telegram_id   = tid,
                amount        = pending["amount"],
                category_name = pending["category"],
                note          = pending["description"],
                image_file_id = pending["image_file_id"],
                ai_confidence = pending["confidence"],
            )
            # Dung ten danh muc thuc su da luu (backend co the fallback ve Khac)
            saved_category = result.get("categoryName") or pending["category"]
            context.user_data.pop("pending_scan", None)
            await query.edit_message_text(
                f"✅ *Đã lưu chi tiêu!*\n\n"
                f"💰 {fmt_vnd(pending['amount'])} – {pending['description']}\n"
                f"📂 {saved_category}\n\n"
                f"_Dùng /report để xem tổng tháng_",
                parse_mode="Markdown"
            )
        except Exception as e:
            logger.error("confirm_scan error: %s", e)
            await query.edit_message_text("❌ Lỗi lưu giao dịch. Thử lại!")


async def edit_amount_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Nhận số tiền sửa từ user sau khi bấm 'Sửa số tiền'."""
    if not context.user_data.get("waiting_edit_amount"):
        return  # Không phải đang chờ edit

    text    = update.message.text.strip()
    tid     = update.effective_user.id
    pending = context.user_data.get("pending_scan")

    if text.lower() == "/cancel" or not pending:
        context.user_data.pop("waiting_edit_amount", None)
        context.user_data.pop("pending_scan", None)
        await update.message.reply_text("❌ Đã hủy.")
        return

    amount = _parse_amount(text)
    if not amount or amount <= 0:
        await update.message.reply_text(
            "❌ Số tiền không hợp lệ. Nhập lại (VD: `45000` hoặc `45k`):",
            parse_mode="Markdown"
        )
        return

    # Cập nhật amount và lưu
    pending["amount"] = amount
    context.user_data.pop("waiting_edit_amount", None)

    try:
        result = await api.confirm_scan(
            telegram_id   = tid,
            amount        = amount,
            category_name = pending["category"],
            note          = pending["description"],
            image_file_id = pending["image_file_id"],
            ai_confidence = pending["confidence"],
        )
        # Dung ten danh muc thuc su da luu (backend co the fallback ve Khac)
        saved_category = result.get("categoryName") or pending["category"]
        context.user_data.pop("pending_scan", None)
        await update.message.reply_text(
            f"✅ *Đã lưu chi tiêu!*\n\n"
            f"💰 {fmt_vnd(amount)} – {pending['description']}\n"
            f"📂 {saved_category}\n\n"
            f"_Dùng /report để xem tổng tháng_",
            parse_mode="Markdown"
        )
    except Exception as e:
        logger.error("edit_amount confirm error: %s", e)
        await update.message.reply_text("❌ Lỗi lưu. Thử lại!")


# ══════════════════════════════════════════════════════════════
#  /setkey  <groq_key>   –  Cài key riêng
#  /setkey               –  Xóa key riêng
# ══════════════════════════════════════════════════════════════

async def setkey_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Cài / xóa Groq API Key riêng của user."""
    if not await _require_registered(update):
        return

    tid  = update.effective_user.id
    args = context.args

    if not args:
        await update.message.reply_text(
            "🔑 *Cài đặt Groq API Key riêng*\n\n"
            "Để cài đặt key riêng (không giới hạn số lần scan):\n"
            "👉 `/setkey gsk_xxxxxxxxxxxxxxx`\n\n"
            "Để xóa key hiện tại (dùng lại quota miễn phí 10 lần/ngày):\n"
            "👉 `/setkey delete` (hoặc `/setkey clear`)\n\n"
            "Lấy key Groq miễn phí tại: https://console.groq.com/keys",
            parse_mode="Markdown"
        )
        return

    action = args[0].strip().lower()

    if action in ("delete", "clear", "remove"):
        try:
            msg = await api.set_groq_key(tid, None)
            await update.message.reply_text(msg)
        except Exception as e:
            logger.error("setkey delete error: %s", e)
            await update.message.reply_text("❌ Lỗi xóa key. Thử lại sau!")
        return

    api_key = args[0].strip()
    if not api_key.startswith("gsk_"):
        await update.message.reply_text(
            "❌ Key không hợp lệ!\n\n"
            "Groq API Key bắt đầu bằng `gsk_`\n"
            "Lấy key miễn phí tại: https://console.groq.com/keys",
            parse_mode="Markdown"
        )
        return

    try:
        msg = await api.set_groq_key(tid, api_key)
        await update.message.reply_text(msg)
    except Exception as e:
        logger.error("setkey error: %s", e)
        await update.message.reply_text("❌ Lỗi cài key. Thử lại sau!")


# ══════════════════════════════════════════════════════════════
#  /keystatus  –  Xem quota AI hôm nay
# ══════════════════════════════════════════════════════════════

async def keystatus_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Xem trạng thái Groq quota."""
    if not await _require_registered(update):
        return

    try:
        status = await api.get_key_status(update.effective_user.id)
        await update.message.reply_text(status["message"])
    except Exception as e:
        logger.error("keystatus error: %s", e)
        await update.message.reply_text("❌ Lỗi kiểm tra quota.")


# ══════════════════════════════════════════════════════════════
#  Helper: Hiện bảng chọn danh mục
# ══════════════════════════════════════════════════════════════

async def _show_category_picker(
        update: Update,
        context: ContextTypes.DEFAULT_TYPE,
        amount: int,
        note: str | None,
        expense_type: str = "EXPENSE"):
    """
    Hiện InlineKeyboard với danh sách danh mục từ DB.
    Mỗi nút = 1 danh mục, bấm vào → lưu giao dịch.
    """
    tid = update.effective_user.id
    try:
        categories = await api.get_categories(tid)
    except Exception:
        categories = []

    # Lọc theo loại giao dịch
    filtered = [c for c in categories if c.get("type") in (expense_type, "BOTH")]

    # Xếp nút thành hàng 2 cột
    buttons, row = [], []
    for cat in filtered:
        icon   = cat.get("icon") or ""
        name   = cat.get("name", "")
        cat_id = cat.get("id") or name
        row.append(InlineKeyboardButton(
            f"{icon} {name}",
            callback_data=f"cat_{cat_id}_{name}"
        ))
        if len(row) == 2:
            buttons.append(row)
            row = []
    if row:
        buttons.append(row)
    buttons.append([InlineKeyboardButton("❌ Hủy", callback_data="cat_cancel")])

    type_label = "💸 Chi tiêu" if expense_type == "EXPENSE" else "💰 Thu nhập"
    if not filtered:
        await update.message.reply_text(
            f"{type_label}: *{fmt_vnd(amount)}*"
            + (f"\n📝 {note}" if note else "")
            + "\n\n⚠️ Bạn chưa có danh mục nào.\n"
            + "Hãy tự thêm danh mục của bạn trước trong `⚙️ Cài đặt` > `Quản lý danh mục`.\n"
            + "AI scan chỉ gán vào các danh mục bạn đã tạo sẵn.",
            parse_mode="Markdown",
        )
        return

    await update.message.reply_text(
        f"{type_label}: *{fmt_vnd(amount)}*"
        + (f"\n📝 {note}" if note else "")
        + "\n\n📂 *Chọn danh mục:*",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(buttons)
    )


# ══════════════════════════════════════════════════════════════
#  Callback: User bấm chọn danh mục
# ══════════════════════════════════════════════════════════════

async def category_callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Xử lý khi user bấm nút chọn danh mục.
    callback_data: "cat_<id>_<name>" hoặc "cat_cancel"
    """
    query = update.callback_query
    await query.answer()

    if query.data == "cat_cancel":
        context.user_data.pop("pending_expense", None)
        await query.edit_message_text("❌ Đã hủy. Không lưu giao dịch.")
        return

    pending = context.user_data.get("pending_expense")
    if not pending:
        await query.edit_message_text("⚠️ Phiên nhập đã hết hạn. Nhập lại lệnh.")
        return

    # Parse callback_data: "cat_<id>_<name>"
    parts    = query.data.split("_", 2)    # ["cat", "<id>", "<name>"]
    cat_name = parts[2] if len(parts) >= 3 else "Khác"

    amount       = pending["amount"]
    note         = pending["note"]
    expense_type = pending["type"]
    tid          = query.from_user.id

    try:
        await api.add_expense(
            telegram_id   = tid,
            type_         = expense_type,
            amount        = amount,
            category_name = cat_name,
            note          = note,
        )
        context.user_data.pop("pending_expense", None)

        sign  = "🔴" if expense_type == "EXPENSE" else "🟢"
        label = "chi tiêu" if expense_type == "EXPENSE" else "thu nhập"
        await query.edit_message_text(
            f"✅ *Đã ghi {label}!*\n\n"
            f"{sign} Số tiền: *{fmt_vnd(amount)}*\n"
            f"📂 Danh mục: {cat_name}\n"
            f"📝 Ghi chú: {note or '—'}\n\n"
            f"_Dùng /report để xem tổng tháng này_",
            parse_mode="Markdown"
        )
    except Exception as e:
        logger.error("category_callback error: %s", e)
        await query.edit_message_text("❌ Lỗi ghi giao dịch. Thử lại sau!")
