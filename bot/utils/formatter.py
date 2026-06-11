# ============================================================
#  Formatter – Format tin nhắn Telegram
#  Chuẩn hóa cách hiển thị dữ liệu cho người dùng
# ============================================================


def format_schedule_today(classes: list[dict]) -> str:
    """
    Format thời khóa biểu hôm nay.

    Args:
        classes: [{"subject": "Java", "room": "B1-301", "start": "07:00", "end": "09:30"}, ...]
    """
    if not classes:
        return "📅 *Hôm nay không có lịch học* 🎉"

    lines = ["📅 *Thời khóa biểu hôm nay:*\n"]
    for c in classes:
        lines.append(
            f"🏫 *{c['subject']}*\n"
            f"   ⏰ {c['start']} – {c['end']}\n"
            f"   📍 Phòng {c['room']}\n"
        )
    return "\n".join(lines)


def format_deadlines(deadlines: list[dict]) -> str:
    """
    Format danh sách deadline sắp tới.

    Args:
        deadlines: [{"title": "Báo cáo Linux", "due_date": "2025-06-15", "days_left": 3}, ...]
    """
    if not deadlines:
        return "✅ *Không có deadline nào sắp tới*"

    lines = ["⏰ *Deadline sắp tới:*\n"]
    for d in deadlines:
        days = d["days_left"]
        emoji = "🔴" if days <= 1 else "🟡" if days <= 3 else "🟢"
        lines.append(f"{emoji} *{d['title']}* — còn {days} ngày")
    return "\n".join(lines)


def format_expense_report(report: dict) -> str:
    """
    Format báo cáo chi tiêu tháng với thanh progress bar.

    Args:
        report: {"month": "6/2025", "categories": [...], "total": ..., "income": ..., "remaining": ...}
    """
    lines = [f"📊 *Báo cáo tháng {report['month']}*\n{'─' * 25}"]

    for cat in report.get("categories", []):
        pct = cat["percentage"]
        bar = make_progress_bar(pct)
        lines.append(f"{cat['icon']} {cat['name']}: {cat['amount']:,}đ  {bar}  {pct}%")

    lines.append(f"{'─' * 25}")
    lines.append(f"💸 Tổng chi:  {report['total']:,}đ")
    lines.append(f"💰 Thu nhập: {report['income']:,}đ")
    lines.append(f"✅ Còn lại:  {report['remaining']:,}đ")
    return "\n".join(lines)


def make_progress_bar(percentage: int, length: int = 10) -> str:
    """Tạo thanh progress bar bằng ký tự Unicode."""
    filled = round(percentage / 100 * length)
    empty = length - filled
    return "█" * filled + "░" * empty


def format_quiz_result(result: dict) -> str:
    """Format kết quả phiên quiz."""
    score = result["score_pct"]
    emoji = "🏆" if score >= 80 else "👍" if score >= 60 else "💪"
    return (
        f"{emoji} *Kết quả phiên ôn tập*\n\n"
        f"✅ Đúng: {result['correct']}/{result['total']}\n"
        f"❌ Sai:  {result['wrong']}/{result['total']}\n"
        f"📊 Điểm: *{score}%*"
    )
