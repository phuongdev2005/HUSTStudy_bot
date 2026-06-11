# ============================================================
#  Keyboards – Inline keyboard buttons Telegram
#  Tạo các menu nút bấm tương tác cho người dùng
# ============================================================

from telegram import InlineKeyboardButton, InlineKeyboardMarkup


def main_menu_keyboard() -> InlineKeyboardMarkup:
    """Menu chính của bot."""
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("📅 Lịch học", callback_data="schedule"),
            InlineKeyboardButton("⏰ Deadline", callback_data="deadline"),
        ],
        [
            InlineKeyboardButton("📝 Lịch thi", callback_data="exam"),
            InlineKeyboardButton("💸 Chi tiêu", callback_data="expense"),
        ],
        [
            InlineKeyboardButton("🧠 Ôn từ vựng", callback_data="quiz"),
            InlineKeyboardButton("📤 Xuất Sheets", callback_data="export"),
        ],
    ])


def report_period_keyboard() -> InlineKeyboardMarkup:
    """Chọn khoảng thời gian báo cáo chi tiêu."""
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("Hôm nay",  callback_data="report_today"),
            InlineKeyboardButton("Tuần này", callback_data="report_week"),
            InlineKeyboardButton("Tháng này", callback_data="report_month"),
        ],
    ])


def export_target_keyboard() -> InlineKeyboardMarkup:
    """Chọn loại dữ liệu cần xuất ra Google Sheets."""
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📅 Thời khóa biểu", callback_data="export_schedule")],
        [InlineKeyboardButton("💸 Báo cáo chi tiêu", callback_data="export_expense")],
        [InlineKeyboardButton("📦 Xuất tất cả", callback_data="export_all")],
    ])


def confirm_keyboard(action: str) -> InlineKeyboardMarkup:
    """Nút xác nhận / huỷ cho các thao tác xóa hoặc reset."""
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("✅ Xác nhận", callback_data=f"confirm_{action}"),
            InlineKeyboardButton("❌ Huỷ",      callback_data="cancel"),
        ],
    ])
