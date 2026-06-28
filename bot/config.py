# ============================================================
#  HUSTStudy Bot – Cấu hình
#  Đọc từ file .env ở thư mục gốc
# ============================================================

import os
from dotenv import load_dotenv

load_dotenv()  # Tự động đọc file .env

# Telegram Bot
BOT_TOKEN    = os.getenv("TELEGRAM_BOT_TOKEN", "")
BOT_USERNAME = os.getenv("TELEGRAM_BOT_USERNAME", "")

# Java Backend API
API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8081/api")

# Groq AI Vision – scan ảnh hóa đơn
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
GROQ_MODEL   = "meta-llama/llama-4-scout-17b-16e-instruct"

# Kiểm tra config bắt buộc
if not BOT_TOKEN:
    raise ValueError("TELEGRAM_BOT_TOKEN chưa được cấu hình trong .env!")
