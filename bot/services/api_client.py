# ============================================================
#  API Client – Gọi Java Backend
#  Tất cả request đến Spring Boot đều đi qua đây
# ============================================================

import httpx
from config import API_BASE_URL


class ApiClient:
    """
    Client gọi Java Spring Boot API.
    Dùng httpx để gửi HTTP request bất đồng bộ (async).
    """

    def __init__(self):
        # Tạo HTTP client với timeout mặc định 10 giây
        self.client = httpx.AsyncClient(
            base_url=API_BASE_URL,
            timeout=10.0
        )

    # ── User API ──────────────────────────────────────────────

    async def register_user(self, telegram_id: int, username: str, full_name: str) -> dict:
        """
        Đăng ký user mới hoặc cập nhật nếu đã tồn tại.
        Gọi khi user dùng lệnh /start.
        """
        response = await self.client.post("/users/register", json={
            "telegramId": telegram_id,
            "username":   username,
            "fullName":   full_name,
        })
        response.raise_for_status()  # Raise lỗi nếu status >= 400
        return response.json()

    async def user_exists(self, telegram_id: int) -> bool:
        """Kiểm tra user đã đăng ký chưa."""
        response = await self.client.get(f"/users/exists/{telegram_id}")
        response.raise_for_status()
        return response.json()

    async def deactivate_user(self, telegram_id: int) -> None:
        """
        User block bot → đánh dấu isActive = false.
        PATCH /users/{telegramId}/deactivate
        """
        r = await self.client.patch(f"/users/{telegram_id}/deactivate")
        r.raise_for_status()

    async def get_categories(self, telegram_id: int) -> list[dict]:
        """Lấy danh sách danh mục (hệ thống + riêng của user)."""
        r = await self.client.get("/expense/categories", params={"telegramId": telegram_id})
        r.raise_for_status()
        return r.json()

    async def add_category(self, telegram_id: int, name: str,
                           icon: str = "📦", type_: str = "EXPENSE") -> dict:
        """Tạo danh mục chi tiêu riêng của user."""
        r = await self.client.post("/expense/categories", json={
            "telegramId": telegram_id,
            "name":       name,
            "icon":       icon,
            "type":       type_,
        })
        r.raise_for_status()
        return r.json()

    async def delete_category(self, telegram_id: int, category_id: int) -> dict:
        """Xóa danh mục riêng của user (không xóa được danh mục hệ thống)."""
        r = await self.client.delete(
            f"/expense/categories/{category_id}",
            params={"telegramId": telegram_id}
        )
        r.raise_for_status()
        return r.json()

    async def update_category(self, telegram_id: int, category_id: int,
                              name: str | None = None, icon: str | None = None) -> dict:
        """Cập nhật tên / icon danh mục riêng của user."""
        r = await self.client.put(
            f"/expense/categories/{category_id}",
            json={
                "telegramId": telegram_id,
                "name":       name,
                "icon":       icon,
            }
        )
        r.raise_for_status()
        return r.json()

    async def delete_expense(self, telegram_id: int, expense_id: int) -> dict:
        """Xóa một giao dịch chi tiêu/thu nhập của user."""
        r = await self.client.delete(
            f"/expense/{expense_id}",
            params={"telegramId": telegram_id},
        )
        r.raise_for_status()
        return r.json()

    async def update_expense(self, telegram_id: int, expense_id: int,
                             amount: int | None = None,
                             category_name: str | None = None,
                             note: str | None = None) -> dict:
        """Cap nhat so tien / danh muc / ghi chu cua giao dich."""
        payload = {"telegramId": telegram_id}
        if amount is not None:
            payload["amount"] = amount
        if category_name is not None:
            payload["categoryName"] = category_name
        if note is not None:
            payload["note"] = note
        r = await self.client.put(f"/expense/{expense_id}", json=payload)
        r.raise_for_status()
        return r.json()


    # ── Schedule / Google Sheet API ───────────────────────────

    async def set_sheet(self, telegram_id: int, sheet_url: str) -> dict:
        """
        Lưu link Google Sheet của user.
        POST /api/schedule/{telegramId}/setsheet
        """
        response = await self.client.post(
            f"/schedule/{telegram_id}/setsheet",
            json={"sheetUrl": sheet_url},
        )
        response.raise_for_status()
        return response.json()

    async def sync_sheet(self, telegram_id: int) -> dict:
        """
        Trigger sync dữ liệu từ Google Sheet vào DB.
        POST /api/schedule/{telegramId}/sync
        Returns: { success, syncedCount, errors, message }
        """
        response = await self.client.post(
            f"/schedule/{telegram_id}/sync",
            timeout=60.0,   # Sync có thể lâu hơn bình thường
        )
        response.raise_for_status()
        return response.json()

    async def get_today_schedule(self, telegram_id: int) -> list[dict]:
        """
        Lấy lịch học hôm nay từ DB.
        GET /api/schedule/{telegramId}/today
        Returns: list of { subjectName, subjectCode, dayOfWeek, startTime, endTime, room, teacher }
        """
        response = await self.client.get(f"/schedule/{telegram_id}/today")
        response.raise_for_status()
        return response.json()

    async def get_week_schedule(self, telegram_id: int) -> list[dict]:
        """
        Lấy toàn bộ lịch học trong tuần từ DB.
        GET /api/schedule/{telegramId}/week
        """
        response = await self.client.get(f"/schedule/{telegram_id}/week")
        response.raise_for_status()
        return response.json()

    # ── Daily Timeline API ───────────────────────────────────

    async def sync_daily_sheet(self, telegram_id: int) -> dict:
        """
        Sync lịch sinh hoạt toàn ngày từ Google Sheet (format 6 cột).
        POST /api/schedule/{telegramId}/sync-daily
        Returns: { success, syncedCount, errors, message }
        """
        response = await self.client.post(
            f"/schedule/{telegram_id}/sync-daily",
            timeout=60.0,
        )
        response.raise_for_status()
        return response.json()

    async def get_notification_settings(self, telegram_id: int) -> dict:
        """Lấy cài đặt thông báo của user."""
        r = await self.client.get(f"/users/{telegram_id}/notifications")
        r.raise_for_status()
        return r.json()

    async def update_notification_settings(self, telegram_id: int, data: dict) -> dict:
        """Cập nhật cài đặt thông báo (chỉ fields có trong data)."""
        r = await self.client.patch(f"/users/{telegram_id}/notifications", json=data)
        r.raise_for_status()
        return r.json()

    async def get_all_users_with_notifications(self) -> list[dict]:
        """Lấy danh sách tất cả user cùng notification settings (dùng cho scheduler)."""
        r = await self.client.get("/users/all-with-notifications")
        r.raise_for_status()
        return r.json()

    async def get_all_daily_schedule(self, telegram_id: int) -> list[dict]:
        """
        Lấy toàn bộ lịch sinh hoạt của user (mọi ngày trong tuần).
        GET /api/schedule/{telegramId}/daily/all
        """
        response = await self.client.get(f"/schedule/{telegram_id}/daily/all")
        response.raise_for_status()
        return response.json()

    async def get_daily_schedule(self, telegram_id: int, day_of_week: int) -> list[dict]:
        """
        Lấy lịch sinh hoạt theo ngày trong tuần.
        GET /api/schedule/{telegramId}/daily?day={day}
        """
        response = await self.client.get(
            f"/schedule/{telegram_id}/daily",
            params={"day": day_of_week},
        )
        response.raise_for_status()
        return response.json()

    # ── Expense / Chi tiêu API ────────────────────────────────

    async def add_expense(self, telegram_id: int, type_: str, amount: int,
                          category_name: str, note: str | None = None) -> dict:
        """Thêm giao dịch chi tiêu / thu nhập nhập tay."""
        r = await self.client.post("/expense/add", json={
            "telegramId":  telegram_id,
            "type":        type_,
            "amount":      amount,
            "categoryName": category_name,
            "note":        note,
        })
        r.raise_for_status()
        return r.json()

    async def confirm_scan(self, telegram_id: int, amount: int, category_name: str,
                           note: str | None, image_file_id: str | None,
                           ai_confidence: float | None) -> dict:
        """Lưu giao dịch sau khi user xác nhận kết quả AI scan."""
        r = await self.client.post("/expense/confirm-scan", json={
            "telegramId":   telegram_id,
            "type":         "EXPENSE",
            "amount":       amount,
            "categoryName": category_name,
            "note":         note,
            "imageFileId":  image_file_id,
            "aiConfidence": ai_confidence,
        })
        r.raise_for_status()
        return r.json()

    async def get_expense_report(self, telegram_id: int,
                                 month: int | None = None, year: int | None = None) -> dict:
        """Lấy báo cáo chi tiêu tháng."""
        params = {"telegramId": telegram_id}
        if month: params["month"] = month
        if year:  params["year"]  = year
        r = await self.client.get("/expense/report", params=params)
        r.raise_for_status()
        return r.json()

    async def get_expense_history(self, telegram_id: int, period: str = "month",
                                  limit: int = 10) -> list[dict]:
        """Lấy lịch sử giao dịch."""
        r = await self.client.get("/expense/history", params={
            "telegramId": telegram_id, "period": period, "limit": limit
        })
        r.raise_for_status()
        return r.json()

    async def set_groq_key(self, telegram_id: int, api_key: str | None) -> str:
        """Cài / xóa Groq API Key riêng của user."""
        r = await self.client.post("/expense/setkey", json={
            "telegramId": telegram_id,
            "apiKey":     api_key,
        })
        r.raise_for_status()
        return r.json()["message"]

    async def get_key_status(self, telegram_id: int) -> dict:
        """Xem trạng thái quota AI của user."""
        r = await self.client.get("/expense/keystatus", params={"telegramId": telegram_id})
        r.raise_for_status()
        return r.json()

    async def reset_expenses(self, telegram_id: int) -> dict:
        """Reset toàn bộ giao dịch chi tiêu của user."""
        r = await self.client.delete("/expense/reset", params={"telegramId": telegram_id})
        r.raise_for_status()
        return r.json()

    # ── Deadline API ──────────────────────────────────────────

    async def get_deadlines(self, telegram_id: int) -> list[dict]:
        """Lấy danh sách deadline sắp tới (chưa done, sắp xếp theo ngày)."""
        r = await self.client.get(f"/deadlines/{telegram_id}")
        r.raise_for_status()
        return r.json()

    async def add_deadline(self, telegram_id: int, title: str,
                           due_date: str, subject: str | None = None) -> dict:
        """Thêm deadline mới."""
        r = await self.client.post("/deadlines", json={
            "telegramId": telegram_id,
            "title":      title,
            "dueDate":    due_date,
            "subject":    subject,
        })
        r.raise_for_status()
        return r.json()

    async def done_deadline(self, telegram_id: int, deadline_id: int) -> dict:
        """Đánh dấu deadline đã hoàn thành."""
        r = await self.client.patch(f"/deadlines/{deadline_id}/done",
                                    params={"telegramId": telegram_id})
        r.raise_for_status()
        return r.json()

    # ── Exam API ──────────────────────────────────────────────

    async def get_exams(self, telegram_id: int) -> list[dict]:
        """Lấy danh sách lịch thi (sắp xếp theo ngày thi)."""
        r = await self.client.get(f"/exams/{telegram_id}")
        r.raise_for_status()
        return r.json()

    async def add_exam(self, telegram_id: int, subject: str, exam_date: str,
                       start_time: str, room: str | None = None,
                       exam_type: str | None = None) -> dict:
        """Thêm lịch thi mới."""
        r = await self.client.post("/exams", json={
            "telegramId":  telegram_id,
            "subject":     subject,
            "examDate":    exam_date,
            "startTime":   start_time,
            "room":        room,
            "examType":    exam_type,
        })
        r.raise_for_status()
        return r.json()

    # ── Vocabulary / Quiz API ─────────────────────────────────

    async def get_next_quiz_word(self, telegram_id: int) -> dict | None:
        """Lấy từ tiếp theo cần ôn (spaced repetition — nextReviewAt gần nhất)."""
        r = await self.client.get(f"/vocabulary/{telegram_id}/next")
        if r.status_code == 204:
            return None
        r.raise_for_status()
        return r.json()

    async def add_word(self, telegram_id: int, word: str, meaning: str,
                       example: str | None = None) -> dict:
        """Thêm từ vựng mới."""
        r = await self.client.post("/vocabulary", json={
            "telegramId": telegram_id,
            "word":       word,
            "meaning":    meaning,
            "example":    example,
        })
        r.raise_for_status()
        return r.json()

    async def get_all_words(self, telegram_id: int) -> list[dict]:
        """Lấy toàn bộ từ vựng của user."""
        r = await self.client.get(f"/vocabulary/{telegram_id}")
        r.raise_for_status()
        return r.json()

    async def submit_quiz_result(self, telegram_id: int,
                                 word_id: int, correct: bool) -> dict:
        """Cập nhật kết quả quiz — tăng/giảm level spaced repetition."""
        r = await self.client.post(f"/vocabulary/{word_id}/review", json={
            "telegramId": telegram_id,
            "correct":    correct,
        })
        r.raise_for_status()
        return r.json()

    async def close(self):
        """Đóng HTTP client khi shutdown."""
        await self.client.aclose()


# Singleton — dùng chung 1 instance trong toàn bộ bot
api = ApiClient()
