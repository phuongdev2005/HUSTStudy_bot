# ============================================================
#  Menu – Keyboard buttons cho HUSTStudy Bot
#  ReplyKeyboard: nút cố định ở đáy màn hình
#  InlineKeyboard: submenu cho từng tính năng
# ============================================================

from telegram import (
    ReplyKeyboardMarkup, KeyboardButton,
    InlineKeyboardMarkup, InlineKeyboardButton,
)

# ══════════════════════════════════════════════════════════════
#  MAIN KEYBOARD — hiển thị cố định ở đáy màn hình
# ══════════════════════════════════════════════════════════════

MAIN_KEYBOARD = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton("📅 Lịch học"),
            KeyboardButton("💸 Chi tiêu"),
            KeyboardButton("📆 Sự kiện"),
        ],
        [
            KeyboardButton("🇬🇧 Tiếng Anh"),
            KeyboardButton("⚙️ Cài đặt"),
        ],
    ],
    resize_keyboard=True,
    input_field_placeholder="Chọn chức năng hoặc nhập lệnh...",
)


# ══════════════════════════════════════════════════════════════
#  INLINE KEYBOARDS — submenu cho từng mục
# ══════════════════════════════════════════════════════════════

def schedule_menu() -> InlineKeyboardMarkup:
    """Submenu Lịch học — lịch sinh hoạt đã bao gồm TKB lớp rồi."""
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("🌅 Hôm nay",          callback_data="schedule_daily_today"),
            InlineKeyboardButton("📆 Cả tuần",           callback_data="schedule_daily_week"),
        ],
        [
            InlineKeyboardButton("🔄 Đồng bộ Sheet",     callback_data="schedule_sync_daily"),
            InlineKeyboardButton("🔗 Cài Google Sheet",  callback_data="schedule_setsheet"),
        ],
    ])


def expense_menu() -> InlineKeyboardMarkup:
    """Submenu Chi tiêu."""
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("➕ Ghi chi tiêu",    callback_data="expense_add"),
            InlineKeyboardButton("💚 Ghi thu nhập",    callback_data="expense_income"),
        ],
        [
            InlineKeyboardButton("📸 Scan hóa đơn",    callback_data="expense_scan_hint"),
            InlineKeyboardButton("📊 Báo cáo tháng",   callback_data="expense_report"),
        ],
        [
            InlineKeyboardButton("⚙️ Quản lý danh mục",  callback_data="expense_manage_cat"),
            InlineKeyboardButton("📥 Xuất file Excel",   callback_data="expense_export_excel"),
        ],
    ])


def events_menu() -> InlineKeyboardMarkup:
    """Submenu Sự kiện — Deadline + Lịch thi + HUST CTSV."""
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("⏰ Deadline sắp tới",  callback_data="events_deadline"),
            InlineKeyboardButton("➕ Thêm deadline",     callback_data="events_add_deadline"),
        ],
        [
            InlineKeyboardButton("📋 Lịch thi sắp tới", callback_data="events_exam"),
            InlineKeyboardButton("➕ Thêm lịch thi",    callback_data="events_add_exam"),
        ],
        [
            InlineKeyboardButton("🏫 Sự kiện HUST CTSV", callback_data="events_hust"),
        ],
    ])


def english_menu() -> InlineKeyboardMarkup:
    """Submenu Tiếng Anh — Từ vựng & Quiz."""
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("🧠 Ôn từ vựng",       callback_data="english_quiz"),
            InlineKeyboardButton("➕ Thêm từ mới",      callback_data="english_add_word"),
        ],
        [
            InlineKeyboardButton("📚 Danh sách từ",     callback_data="english_words"),
        ],
    ])


def settings_menu() -> InlineKeyboardMarkup:
    """Submenu Cài đặt."""
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("🔔 Thông báo lịch",     callback_data="settings_notify"),
        ],
        [
            InlineKeyboardButton("🔗 Cài Google Sheet",   callback_data="settings_setsheet"),
        ],
        [
            InlineKeyboardButton("🤖 Cài Groq API Key",   callback_data="settings_setkey"),
            InlineKeyboardButton("📊 Xem quota AI",       callback_data="settings_keystatus"),
        ],
    ])


def report_menu() -> InlineKeyboardMarkup:
    """Submenu Báo cáo."""
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("💸 Chi tiêu tháng",    callback_data="report_expense"),
            InlineKeyboardButton("📋 Lịch sử chi tiêu",  callback_data="report_history"),
        ],
        [
            InlineKeyboardButton("🌅 Lịch hôm nay",      callback_data="report_daily"),
            InlineKeyboardButton("⏰ Deadline sắp tới",  callback_data="report_deadline"),
        ],
        [
            InlineKeyboardButton("📋 Lịch thi sắp tới",  callback_data="report_exam"),
        ],
    ])


# ══════════════════════════════════════════════════════════════
#  Map text button → handler action
# ══════════════════════════════════════════════════════════════

BUTTON_TEXT_MAP = {
    "📅 Lịch học":   "menu_schedule",
    "💸 Chi tiêu":   "menu_expense",
    "📆 Sự kiện":    "menu_events",
    "🇬🇧 Tiếng Anh": "menu_english",
    "⚙️ Cài đặt":   "menu_settings",
}
