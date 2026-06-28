# ─────────────────────────────────────────────────────────────
#  Python Bot – Dockerfile
# ─────────────────────────────────────────────────────────────
FROM python:3.11-slim

WORKDIR /app

# Cài dependencies trước (tận dụng Docker layer cache)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy toàn bộ source bot
COPY . .

CMD ["python", "main.py"]
