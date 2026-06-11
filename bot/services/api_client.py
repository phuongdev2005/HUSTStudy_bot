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

    async def close(self):
        """Đóng HTTP client khi shutdown."""
        await self.client.aclose()


# Singleton — dùng chung 1 instance trong toàn bộ bot
api = ApiClient()
