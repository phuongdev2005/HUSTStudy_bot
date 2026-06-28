# HUSTStudy Bot

Telegram bot hỗ trợ quản lý học tập và chi tiêu cho sinh viên HUST.

## Tổng quan

Repo hiện tại gồm 2 thành phần chính:

- `bot/`: Python Telegram Bot, nhận lệnh từ Telegram và gọi backend.
- `backend/`: Spring Boot REST API, xử lý nghiệp vụ và làm việc với MySQL, Google Sheets.

Hệ thống lưu dữ liệu trong MySQL, đồng bộ một số dữ liệu học tập sang Google Sheets, và có các tác vụ định kỳ bằng scheduler.

## Tính năng chính

### Học tập

- Quản lý thời khóa biểu và lịch sinh hoạt.
- Đồng bộ lịch sinh hoạt từ Google Sheets.
- Xem lịch hôm nay và cả tuần.
- Quản lý deadline.
- Quản lý lịch thi.
- Theo dõi sự kiện HUST CTSV.

### Từ vựng tiếng Anh

- Thêm từ vựng mới.
- Ôn tập bằng lệnh quiz.
- Xem danh sách từ đã lưu.

### Chi tiêu

- Ghi chi tiêu và thu nhập nhanh ngay trong Telegram.
- Xem báo cáo chi tiêu theo tháng.
- Quản lý danh mục chi tiêu.
- Quét hóa đơn bằng ảnh với AI.
- Cấu hình Groq API key riêng cho từng user.
- Kiểm tra trạng thái/quota API key.

### Cài đặt

- Lưu Google Sheet cá nhân cho từng user.
- Cấu hình thông báo.
- Hỗ trợ thao tác qua nút menu và command.

## Kiến trúc

```text
Telegram User
    |
    v
Python Telegram Bot
    |
    v
Spring Boot Backend API
    |
    +--> MySQL
    +--> Google Sheets API
    +--> Scheduler
```

- Bot Python xử lý giao diện chat, command, callback button.
- Backend Java xử lý dữ liệu, CRUD, sync sheet, báo cáo và lịch.
- MySQL lưu toàn bộ dữ liệu chính.
- Scheduler dùng cho các job định kỳ.

## Command

### Khởi động và trợ giúp

- `/start`
- `/help`

### Chi tiêu

- `/addexpense <số_tiền> [ghi chú]`
- `/addincome <số_tiền> [ghi chú]`
- `/report`
- `/setkey <groq_key>`
- `/setkey delete`
- `/setkey clear`
- `/keystatus`

### Lịch học và lịch sinh hoạt

- `/setsheet <link_google_sheet>`
- `/daily`
- `/dailyweek`
- `/syncdaily`

### Deadline

- `/deadline`
- `/adddeadline <tiêu_đề> <YYYY-MM-DD> [môn_học]`
- `/donedl <id>`

### Lịch thi

- `/exam`
- `/addexam <tên_môn> <YYYY-MM-DD> [HH:MM]`

### Từ vựng

- `/quiz`
- `/addword <english> - <vietnamese>`
- `/words`

### Thông báo và sự kiện

- `/notifysettings`
- `/hustevents`

## Menu trong bot

Bot có menu nút bấm ở đáy màn hình cho các nhóm chức năng:

- Lịch học
- Chi tiêu
- Sự kiện
- Tiếng Anh
- Cài đặt

Các nút này gọi lại đúng các command/tác vụ tương ứng.

## Yêu cầu hệ thống

- Python 3.11+ cho bot.
- Java 17+ cho backend.
- MySQL 8+.
- Docker và Docker Compose nếu muốn chạy theo container.
- Một Telegram bot token từ BotFather.
- Google Sheets API credentials nếu dùng đồng bộ sheet.
- Groq API key nếu dùng scan hóa đơn bằng ảnh.

## Cấu hình môi trường

Tạo file `.env` từ `.env.example`:

```env
DB_HOST=localhost
DB_PORT=3306
DB_NAME=huststudy_bot
DB_USER=studybot
DB_PASSWORD=your_db_password_here
DB_ROOT_PASSWORD=your_root_password_here

SERVER_PORT=8081

GOOGLE_CREDENTIALS_PATH=classpath:google-credentials.json
GOOGLE_SPREADSHEET_ID=your_spreadsheet_id_here

TELEGRAM_BOT_TOKEN=your_bot_token_here
TELEGRAM_BOT_USERNAME=your_bot_username_here
```

Ở phía bot Python, các biến chính đang được đọc là:

- `TELEGRAM_BOT_TOKEN`
- `TELEGRAM_BOT_USERNAME`
- `API_BASE_URL`
- `GROQ_API_KEY`

## Chạy bằng Docker

1. Tạo file `.env`.
2. Đảm bảo backend có cấu hình Google Sheets/Groq nếu cần.
3. Chạy:

```bash
docker compose up --build
```

Mặc định compose sẽ khởi chạy:

- MySQL
- Backend Spring Boot
- Telegram bot Python

Nếu muốn mở thêm phpMyAdmin cho môi trường dev:

```bash
docker compose --profile dev up --build
```

phpMyAdmin sẽ chạy tại `http://localhost:8888`.

## Chạy thủ công

### Backend

```bash
cd backend
mvn spring-boot:run
```

### Bot

```bash
cd bot
pip install -r requirements.txt
python main.py
```

## Dữ liệu và migration

Backend dùng Flyway để quản lý schema database. Các file migration nằm trong:

`backend/src/main/resources/db/migration`

## Ghi chú triển khai

- Backend chạy với context path `/api`.
- Bot mặc định gọi backend qua `API_BASE_URL`.
- Scheduler được bật trong backend để chạy các job định kỳ.

## Cấu trúc thư mục

```text
.
├── backend/        # Spring Boot API
├── bot/            # Telegram bot bằng Python
├── docker-compose.yml
├── .env.example
└── README.md
```

## Tình trạng dự án

Đây là README đã được cập nhật theo code hiện tại trong repo. Nếu bạn muốn, tôi có thể tiếp tục:

1. Viết thêm mục “Hướng dẫn sử dụng” cho từng lệnh.
2. Bổ sung sơ đồ database hoặc API endpoints.
3. Rút gọn README theo kiểu ngắn gọn, dễ dùng cho GitHub.
