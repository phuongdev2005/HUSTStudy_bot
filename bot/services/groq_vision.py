# ============================================================
#  Groq Vision Service – Nhận diện ảnh hóa đơn / bill
#  Dùng Groq API (meta-llama/llama-4-scout-17b-16e-instruct)
#  Free tier: 1,000 ảnh/ngày
# ============================================================

import base64
import json
import logging

import httpx

from config import GROQ_API_KEY, GROQ_MODEL

logger = logging.getLogger(__name__)

GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"

SCAN_PROMPT = (
    "Phân tích hóa đơn/biên lai trong ảnh và trả về JSON:\n"
    '{"amount": <tổng tiền thanh toán cuối cùng, số nguyên, không dấu phẩy>,\n'
    '"description": "<Liệt kê tất cả sản phẩm/dịch vụ mua trong hóa đơn kèm số lượng và giá của chúng, ví dụ: 2 Cơm tấm (70k) + 1 Pepsi (15k). Hãy viết ngắn gọn, súc tích và ngăn cách bằng dấu cộng (+)>",\n'
    '"category": "<một tên danh mục ngắn, nên trùng với cách user thường đặt, ví dụ: Ăn uống, Xăng xe, Học tập, Mua sắm, Di chuyển, Giải trí, Sức khỏe, Khác>",\n'
    '"merchant": "<tên cửa hàng nếu đọc được, không thì null>",\n'
    '"type": "EXPENSE",\n'
    '"confidence": <0.0-1.0>}\n'
    "Chỉ trả về JSON thuần, không markdown, không giải thích."
)


async def scan_bill_image(image_bytes: bytes, api_key: str | None = None) -> dict:
    """
    Gửi ảnh lên Groq Vision và trả về dict kết quả.

    Args:
        image_bytes: Bytes của ảnh (JPEG/PNG)
        api_key: Groq API key (dùng key riêng của user nếu có, fallback về owner key)

    Returns:
        dict với keys: success, amount, description, category, merchant, type, confidence, error
    """
    key = api_key or GROQ_API_KEY
    if not key:
        return {"success": False, "error": "Chưa cấu hình Groq API Key."}

    img_b64 = base64.b64encode(image_bytes).decode()
    # Detect format (JPEG vs PNG)
    mime = "image/png" if image_bytes[:4] == b"\x89PNG" else "image/jpeg"

    payload = {
        "model": GROQ_MODEL,
        "messages": [{
            "role": "user",
            "content": [
                {"type": "image_url", "image_url": {"url": f"data:{mime};base64,{img_b64}"}},
                {"type": "text", "text": SCAN_PROMPT},
            ],
        }],
        "max_tokens": 300,
        "temperature": 0.1,
    }

    headers = {
        "Authorization": f"Bearer {key}",
        "Content-Type": "application/json",
    }

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            r = await client.post(GROQ_URL, headers=headers, json=payload)

        if r.status_code != 200:
            logger.error("Groq API error %s: %s", r.status_code, r.text[:200])
            return {"success": False, "error": f"Groq API lỗi {r.status_code}"}

        raw = r.json()["choices"][0]["message"]["content"].strip()

        # Bóc JSON từ response (đôi khi model wrap trong ```json ```)
        if "```" in raw:
            raw = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:]

        result = json.loads(raw)
        result["success"] = True
        return result

    except json.JSONDecodeError as e:
        logger.error("Cannot parse Groq response: %s", e)
        return {"success": False, "error": "Không thể đọc kết quả từ AI."}
    except Exception as e:
        logger.error("Groq Vision error: %s", e)
        return {"success": False, "error": f"Lỗi kết nối AI: {e}"}
