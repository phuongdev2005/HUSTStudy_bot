# ============================================================
#  HUSTStudy Telegram Bot – Entry Point
# ============================================================

import logging
from telegram import BotCommand, Update
from telegram.ext import (
    Application, CommandHandler, MessageHandler,
    CallbackQueryHandler, ChatMemberHandler, filters, ContextTypes,
)

from config import BOT_TOKEN
from handlers.start import start_handler
from handlers.expense import (
    addexpense_handler, addincome_handler,
    report_handler, photo_handler,
    scan_callback_handler, edit_amount_handler,
    setkey_handler, keystatus_handler,
    category_callback_handler,
)
from handlers.deadline import (
    deadline_handler, adddeadline_handler,
    donedl_handler, deadline_callback,
)
from handlers.exam import (
    exam_handler, addexam_handler, exam_callback,
)
from handlers.quiz import (
    quiz_handler, addword_handler,
    words_handler, quiz_callback,
)
from handlers.daily import (
    daily_handler, syncdaily_handler,
    dailyweek_handler, daily_callback,
)
from handlers.notify_settings import (
    notify_settings_handler, notify_callback, notify_input_handler,
)
from handlers.hust_events import hustevents_handler, hust_callback
from handlers.menu_handler import (
    button_handler, menu_callback, expense_amount_input_handler,
    new_category_input_handler, setsheet_input_handler, setsheet_handler,
    edit_category_name_input_handler, edit_category_icon_input_handler,
    editcat_callback, editexp_callback, edit_expense_input_handler,
    quick_expense_input_handler, _HELP_TEXT
)
from handlers.menu import BUTTON_TEXT_MAP, MAIN_KEYBOARD
from services.api_client import api
from services.scheduler import setup_scheduler

logging.basicConfig(
    format="%(asctime)s [%(levelname)s] %(name)s – %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)


async def help_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """/help — Hiển thị hướng dẫn sử dụng."""
    await update.message.reply_text(
        _HELP_TEXT,
        parse_mode="Markdown",
        reply_markup=MAIN_KEYBOARD
    )


async def post_init(application: Application) -> None:
    await application.bot.set_my_commands([
        BotCommand("start", "Bắt đầu & Mở menu chính"),
        BotCommand("help",  "Xem hướng dẫn sử dụng"),
    ])
    # Khởi động các scheduled notifications
    setup_scheduler(application)
    logger.info("✅ Bot commands menu đã được cập nhật")


async def post_shutdown(application: Application) -> None:
    await api.close()
    logger.info("Bot đã tắt.")


def main():
    logger.info("🚀 Đang khởi động HUSTStudy Bot...")

    app = (
        Application.builder()
        .token(BOT_TOKEN)
        .post_init(post_init)
        .post_shutdown(post_shutdown)
        .build()
    )

    # ── Commands ──────────────────────────────────────────────
    app.add_handler(CommandHandler("start",       start_handler))
    app.add_handler(CommandHandler("help",        help_handler))
    app.add_handler(CommandHandler("setsheet",    setsheet_handler))

    # Chi tiêu
    app.add_handler(CommandHandler("addexpense",  addexpense_handler))
    app.add_handler(CommandHandler("addincome",   addincome_handler))
    app.add_handler(CommandHandler("report",      report_handler))
    app.add_handler(CommandHandler("setkey",      setkey_handler))
    app.add_handler(CommandHandler("keystatus",   keystatus_handler))

    # Deadline
    app.add_handler(CommandHandler("deadline",    deadline_handler))
    app.add_handler(CommandHandler("adddeadline", adddeadline_handler))
    app.add_handler(CommandHandler("donedl",      donedl_handler))

    # Lịch thi
    app.add_handler(CommandHandler("exam",        exam_handler))
    app.add_handler(CommandHandler("addexam",     addexam_handler))

    # Từ vựng / Quiz
    app.add_handler(CommandHandler("quiz",        quiz_handler))
    app.add_handler(CommandHandler("addword",     addword_handler))
    app.add_handler(CommandHandler("words",       words_handler))

    # Lịch sinh hoạt
    app.add_handler(CommandHandler("daily",       daily_handler))
    app.add_handler(CommandHandler("dailyweek",   dailyweek_handler))
    app.add_handler(CommandHandler("syncdaily",   syncdaily_handler))

    # Thông báo cài đặt
    app.add_handler(CommandHandler("notifysettings", notify_settings_handler))

    # Sự kiện HUST CTSV
    app.add_handler(CommandHandler("hustevents",  hustevents_handler))

    # ── Ảnh hóa đơn (scan AI) ────────────────────────────────
    app.add_handler(MessageHandler(filters.PHOTO, photo_handler))

    # ── InlineKeyboard callbacks ────────────────────────────────────
    app.add_handler(CallbackQueryHandler(scan_callback_handler,     pattern=r"^scan_"))
    app.add_handler(CallbackQueryHandler(category_callback_handler, pattern=r"^cat_"))
    app.add_handler(CallbackQueryHandler(deadline_callback,         pattern=r"^dl_"))
    app.add_handler(CallbackQueryHandler(exam_callback,             pattern=r"^exam_"))
    app.add_handler(CallbackQueryHandler(quiz_callback,             pattern=r"^quiz_"))

    # Xóa danh mục riêng (delcat_<id>)
    async def delcat_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        await query.answer()
        cat_id = int(query.data.split("_", 1)[1])
        tid    = query.from_user.id
        try:
            await api.delete_category(tid, cat_id)
            await query.answer("✅ Đã xóa danh mục", show_alert=True)
            # Làm mới danh sách
            from handlers.menu_handler import _cb_manage_categories
            await _cb_manage_categories(query, tid, context)
        except Exception as e:
            await query.answer(f"❌ {e}", show_alert=True)

    app.add_handler(CallbackQueryHandler(delcat_callback, pattern=r"^delcat_"))
    app.add_handler(CallbackQueryHandler(editcat_callback, pattern=r"^editcat_"))
    app.add_handler(CallbackQueryHandler(editexp_callback, pattern=r"^editexp_\d+$"))
    async def catdetail_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        await query.answer()
        cat_id = int(query.data.split("_", 1)[1])
        from handlers.menu_handler import _cb_category_detail
        await _cb_category_detail(query, query.from_user.id, cat_id)

    app.add_handler(CallbackQueryHandler(catdetail_callback, pattern=r"^catdetail_\d+$"))
    app.add_handler(CallbackQueryHandler(daily_callback,         pattern=r"^daily_"))
    app.add_handler(CallbackQueryHandler(notify_callback,        pattern=r"^notify_"))
    app.add_handler(CallbackQueryHandler(hust_callback,          pattern=r"^hust_"))
    async def deleteexp_cat_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        await query.answer()
        parts = query.data.split("_")
        cat_id = int(parts[2])
        expense_id = int(parts[3])
        tid = query.from_user.id
        try:
            await api.delete_expense(tid, expense_id)
            await query.answer("Đã xóa giao dịch", show_alert=True)
            from handlers.menu_handler import _cb_category_detail
            await _cb_category_detail(query, tid, cat_id)
        except Exception as e:
            await query.answer(f"❌ {e}", show_alert=True)

    app.add_handler(CallbackQueryHandler(deleteexp_cat_callback, pattern=r"^deleteexp_cat_\d+_\d+$"))
    async def deleteexp_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        await query.answer()
        tid = query.from_user.id
        expense_id = int(query.data.split("_", 1)[1])
        try:
            await api.delete_expense(tid, expense_id)
            await query.answer("Đã xóa giao dịch", show_alert=True)
            from handlers.menu_handler import _cb_history
            await _cb_history(query, tid)
        except Exception as e:
            await query.answer(f"❌ {e}", show_alert=True)

    app.add_handler(CallbackQueryHandler(deleteexp_callback, pattern=r"^deleteexp_\d+$"))
    app.add_handler(CallbackQueryHandler(
        menu_callback,
        pattern=r"^(schedule|expense|events|english|report|settings)_"
    ))

    # ── ReplyKeyboard — nút đáy màn hình ─────────────────────────
    btn_pattern = "^(" + "|".join(BUTTON_TEXT_MAP.keys()) + ")$"
    app.add_handler(MessageHandler(
        filters.TEXT & filters.Regex(btn_pattern),
        button_handler,
    ))

    # ── Text thường ──────────────────────────────────────────────

    async def text_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
        if await edit_expense_input_handler(update, context):
            return
        # Ưu tiên: ghi chi tiêu nhanh theo cú pháp Số tiền | Danh mục | Ghi chú
        if await quick_expense_input_handler(update, context):
            return
        # Ưu tiên: nhập số tiền sau khi bấm nút menu chi tiêu
        if await expense_amount_input_handler(update, context):
            return
        # Ưu tiên: nhập tên danh mục mới
        if await new_category_input_handler(update, context):
            return
        # Ưu tiên: sửa tên danh mục
        if await edit_category_name_input_handler(update, context):
            return
        # Ưu tiên: sửa icon danh mục
        if await edit_category_icon_input_handler(update, context):
            return
        # Ưu tiên: paste link Google Sheet
        if await setsheet_input_handler(update, context):
            return
        # Nhường xử lý cho notify_input_handler
        handled = await notify_input_handler(update, context)
        if not handled:
            await edit_amount_handler(update, context)

    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, text_handler))

    # ── Block / Unblock Bot ───────────────────────────────────
    async def chat_member_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """
        Lắng nghe sự kiện user block / unblock bot.
        - kicked  → user vừa block bot → deactivate
        - member  → user unblock (hiếm, thường đi kèm /start)
        """
        my_chat_member = update.my_chat_member
        if not my_chat_member:
            return
        new_status = my_chat_member.new_chat_member.status
        telegram_id = my_chat_member.from_user.id
        if new_status == "kicked":
            logger.info(f"🚫 User {telegram_id} đã block bot → deactivate")
            try:
                await api.deactivate_user(telegram_id)
            except Exception as e:
                logger.warning(f"⚠️ deactivate_user lỗi: {e}")

    app.add_handler(ChatMemberHandler(chat_member_handler, ChatMemberHandler.MY_CHAT_MEMBER))

    logger.info("Bot đang chạy... Nhấn Ctrl+C để dừng.")
    app.run_polling(drop_pending_updates=True, allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
