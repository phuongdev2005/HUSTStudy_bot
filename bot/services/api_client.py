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

    async def get_user(self, telegram_id: int) -> dict | None:
        """
        Lấy thông tin user. Trả về None nếu chưa đăng ký.
        """
        response = await self.client.get(f"/users/telegram/{telegram_id}")
        if response.status_code == 404:
            return None
        response.raise_for_status()
        return response.json()

    async def user_exists(self, telegram_id: int) -> bool:
        """Kiểm tra user đã đăng ký chưa."""
        response = await self.client.get(f"/users/exists/{telegram_id}")
        response.raise_for_status()
        return response.json()

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

    async def close(self):
        """Đóng HTTP client khi shutdown."""
        await self.client.aclose()


# Singleton — dùng chung 1 instance trong toàn bộ bot
api = ApiClient()
