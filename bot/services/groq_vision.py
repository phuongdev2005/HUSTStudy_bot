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

def get_scan_prompt(categories: list[str] | None = None) -> str:
    """Tạo prompt scan ảnh chứa danh mục của user."""
    safe_categories = [c.strip() for c in (categories or []) if c and c.strip()]
    if "Khác" not in safe_categories:
        safe_categories.append("Khác")
    cat_list = ", ".join(safe_categories)
    food_rule = (
        'Nếu danh sách có danh mục "Ăn uống" thì mọi món ăn, đồ uống, nhà hàng, quán ăn, '
        'cafe, nước, bia, cơm, bún, phở, hải sản, rau, thịt, cá, tôm phải chọn "Ăn uống"; '
        'KHÔNG được chọn "Khác" cho các món này.'
        if "Ăn uống" in safe_categories else ""
    )
    return (
        "Phân tích hóa đơn/biên lai trong ảnh và trả về JSON thuần.\n"
        "QUAN TRỌNG: Không gộp các sản phẩm thành một mô tả chung. "
        "Hãy tách từng dòng hàng/món thành từng phần tử trong items.\n"
        "amount của từng item là THÀNH TIỀN của dòng đó bằng VND, không phải tổng hóa đơn nếu dòng chỉ là một món.\n"
        "Nếu hóa đơn ghi đơn giá và số lượng thì amount = quantity * unitPrice.\n"
        "Nếu không đọc được quantity thì dùng 1. Nếu không đọc được unitPrice thì để null nhưng vẫn cố đọc amount.\n"
        f"Mỗi item phải có category thuộc đúng một trong các danh mục user đã tạo: [{cat_list}]. "
        "Luôn ưu tiên danh mục cụ thể nhất trong danh sách. Chỉ dùng Khác khi item thật sự không phù hợp với bất kỳ danh mục nào khác. "
        f"{food_rule}\n\n"
        "{\n"
        '  "amount": <tổng tiền thanh toán cuối cùng, số nguyên VND>,\n'
        '  "description": "<mô tả ngắn hóa đơn>",\n'
        f'  "category": "<danh mục tổng quan thuộc [{cat_list}], fallback Khác>",\n'
        '"merchant": "<tên cửa hàng nếu đọc được, không thì null>",\n'
        '"type": "EXPENSE",\n'
        '"confidence": <0.0-1.0>,\n'
        '  "items": [\n'
        '    {"name": "<tên món/hàng>", "quantity": <số lượng>, "unitPrice": <đơn giá VND hoặc null>, "amount": <thành tiền VND>, "category": "<danh mục>", "note": "<ghi chú nếu có>"}\n'
        "  ]\n"
        "}\n"
        "Chỉ trả về JSON thuần, không markdown, không giải thích."
    )


async def scan_bill_image(image_bytes: bytes, categories: list[str] | None = None, api_key: str | None = None) -> dict:
    """
    Gửi ảnh lên Groq Vision và trả về dict kết quả.

    Args:
        image_bytes: Bytes của ảnh (JPEG/PNG)
        categories: Danh sách danh mục thực tế của user để AI phân loại đúng
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
                {"type": "text", "text": get_scan_prompt(categories)},
            ],
        }],
        "max_tokens": 1200,
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
        logger.info("Groq raw response: %s", raw)

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
