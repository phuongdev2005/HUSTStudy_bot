# HUSTStudy Bot

Telegram bot hỗ trợ quản lý học tập và chi tiêu cho sinh viên HUST.

## Tổng quan

Repo hiện tại gồm 2 thành phần chính:

- `bot/`: Python Telegram Bot, nhận lệnh từ Telegram và gọi backend.
- `backend/`: Spring Boot REST API, xử lý nghiệp vụ và làm việc với MySQL, Google Sheets.

Hệ thống lưu dữ liệu trong MySQL, đồng bộ một số dữ liệu học tập/sinh hoạt từ Google Sheets của từng user, và có các tác vụ định kỳ bằng scheduler.

## Tính năng chính

### Học tập & Sinh hoạt

- Quản lý thời khóa biểu và lịch sinh hoạt cá nhân.
- Đồng bộ lịch học/lịch sinh hoạt tự động từ Google Sheets cá nhân.
- Xem lịch học hôm nay và cả tuần trực tiếp trên bot.
- Quản lý deadline học tập.
- Quản lý lịch thi sắp tới.
- Tự động theo dõi và cập nhật sự kiện HUST CTSV để tự động tạo deadline mới.

### Từ vựng tiếng Anh (Spaced Repetition)

- Thêm từ vựng mới cùng nghĩa và ví dụ.
- Ôn tập từ vựng ngẫu nhiên qua các câu hỏi Quiz.
- Thuật toán ôn tập dựa trên Spaced Repetition (Lặp lại ngắt quãng) để tăng hiệu quả ghi nhớ.
- Xem danh sách từ đã lưu.

### Quản lý Chi tiêu

- Ghi nhận chi tiêu và thu nhập nhanh chóng bằng tin nhắn thường hoặc câu lệnh.
- Xem báo cáo chi tiêu trực quan theo từng tháng.
- Quản lý danh mục chi tiêu cá nhân (Thêm/Sửa/Xóa tên, icon danh mục).
- Quét hóa đơn bằng ảnh sử dụng AI (Groq API Vision) để tự động bóc tách số tiền, mô tả và phân loại danh mục.
- Cấu hình Groq API key riêng cho từng user để dùng không giới hạn quota.

### Cài đặt cá nhân

- Lưu Google Sheet cá nhân cho từng user.
- Cấu hình bật/tắt nhận thông báo (Lịch học, deadline, lịch thi, bản tin chào buổi sáng, sự kiện HUST).

## Kiến trúc hệ thống

```text
Telegram User
    |
    v
Python Telegram Bot (python-telegram-bot)
    | (HTTP REST API)
    v
Spring Boot Backend API
    |
    +--> MySQL (Lưu trữ quan hệ chính)
    +--> Google Sheets API (Sync lịch)
    +--> APScheduler (Thông báo tự động)
```

- **Bot Python**: Xử lý giao diện chat, bàn phím ReplyKeyboard, InlineKeyboard callbacks, xử lý ảnh hóa đơn gửi lên qua Groq Vision.
- **Backend Java**: Xử lý logic nghiệp vụ, kết nối MySQL thông qua Spring Data JPA, cung cấp API endpoint cho bot.
- **MySQL**: Lưu trữ thông tin người dùng, cài đặt thông báo, danh sách chi tiêu, danh mục, deadline, lịch thi và từ vựng.
- **Scheduler**: Gửi thông báo nhắc nhở lịch học trước giờ học, nhắc nhở deadline/lịch thi hàng ngày lúc 08:00 sáng.

## Các lệnh trên Bot (Commands)

### Khởi động và trợ giúp
- `/start` - Khởi động bot, đăng ký tài khoản (nếu chưa có) và hiển thị menu chính.
- `/help` - Xem hướng dẫn sử dụng chi tiết.

### Quản lý chi tiêu
- `/addexpense <số_tiền> [ghi chú]` - Ghi nhanh chi tiêu tay (VD: `/addexpense 35k cơm trưa`).
- `/addincome <số_tiền> [ghi chú]` - Ghi nhanh thu nhập tay.
- `/report` - Xem báo cáo chi tiêu tháng này.
- `/setkey <groq_key>` - Cài đặt API key Groq cá nhân.
- `/setkey delete` (hoặc `clear`) - Xóa API key Groq cá nhân, quay lại dùng quota miễn phí.
- `/keystatus` - Xem số lượt scan hóa đơn miễn phí còn lại trong ngày.

### Lịch học & Google Sheet
- `/setsheet <link_google_sheet>` - Cài đặt link Google Sheet của bạn.
- `/daily` - Xem lịch sinh hoạt hôm nay.
- `/dailyweek` - Xem lịch sinh hoạt cả tuần.
- `/syncdaily` - Đồng bộ lại lịch học và lịch sinh hoạt từ Google Sheet vào DB.

### Deadline
- `/deadline` - Xem danh sách deadline hiện có.
- `/adddeadline <tiêu_đề> <YYYY-MM-DD> [môn_học]` - Thêm deadline mới.
- `/donedl <id>` - Đánh dấu hoàn thành deadline.

### Lịch thi
- `/exam` - Xem danh sách lịch thi.
- `/addexam <tên_môn> <YYYY-MM-DD> [HH:MM]` - Thêm lịch thi mới.

### Học từ vựng
- `/quiz` - Bắt đầu làm Quiz ôn tập từ vựng.
- `/addword <english> - <vietnamese>` - Thêm từ vựng mới kèm nghĩa.
- `/words` - Xem danh sách tất cả từ vựng đang học.

### Thông báo & Sự kiện
- `/notifysettings` - Mở menu cài đặt bật/tắt nhận thông báo.
- `/hustevents` - Xem các sự kiện CTSV HUST sắp diễn ra.

## Yêu cầu hệ thống

- **Python 3.11+**
- **Java 17+ (Spring Boot 3.x)**
- **MySQL 8.0+**
- **Docker & Docker Compose** (Khuyên dùng để cài đặt nhanh)
- API keys:
  - Một Telegram Bot Token từ [@BotFather](https://t.me/BotFather).
  - Một Google Sheets API Key (hoặc Service Account) cấu hình public xem sheet.
  - Một Groq API Key (tùy chọn, tạo miễn phí tại [Groq Console](https://console.groq.com/keys)).

## Cấu hình môi trường

Tạo file `.env` tại thư mục gốc của dự án từ file mẫu `.env.example`:

```env
# Database MySQL
DB_HOST=localhost
DB_PORT=3306
DB_NAME=huststudy_bot
DB_USER=studybot
DB_PASSWORD=your_db_password_here
DB_ROOT_PASSWORD=your_root_password_here

# Backend Port
SERVER_PORT=8081

# Google Sheets API Config
GOOGLE_API_KEY=your_google_api_key_here
GOOGLE_SPREADSHEET_ID=your_spreadsheet_id_here

# Telegram Bot Config
TELEGRAM_BOT_TOKEN=your_bot_token_here
TELEGRAM_BOT_USERNAME=your_bot_username_here

# Python Bot Config (gọi Backend)
API_BASE_URL=http://localhost:8081/api
```

## Hướng dẫn cài đặt nhanh bằng Docker

1. Clone repository về máy.
2. Tạo file `.env` tại thư mục gốc và điền các giá trị thích hợp.
3. Khởi chạy toàn bộ hệ thống bằng Docker Compose:

```bash
docker compose up --build -d
```

Lệnh trên sẽ tự động dựng và chạy 3 container:
- `mysql`: Database MySQL 8.0
- `backend`: Java Spring Boot Backend API
- `bot`: Python Telegram Bot Client

### phpMyAdmin (Môi trường Dev)
Nếu bạn muốn truy cập giao diện quản trị database (phpMyAdmin) khi đang lập trình:

```bash
docker compose --profile dev up --build -d
```
Giao diện phpMyAdmin sẽ khả dụng tại địa chỉ `http://localhost:8888`.

## Hướng dẫn chạy thủ công (Không dùng Docker)

### 1. Cài đặt Database
- Tạo một database MySQL tên là `huststudy_bot`.
- Tạo user và grant toàn quyền cho user đó trên database vừa tạo.

### 2. Chạy Backend (Spring Boot)
Di chuyển vào thư mục backend và chạy ứng dụng:
```bash
cd backend
mvn spring-boot:run
```
Flyway sẽ tự động chạy các tệp migration trong `backend/src/main/resources/db/migration` để tạo bảng dữ liệu.

### 3. Chạy Telegram Bot (Python)
Di chuyển vào thư mục bot, cài đặt thư viện và chạy:
```bash
cd bot
pip install -r requirements.txt
python main.py
```

## Cấu trúc thư mục dự án

```text
.
├── backend/            # Mã nguồn Java Spring Boot Backend
│   ├── src/            # Logic nghiệp vụ (Controller, Service, Repository, Entity)
│   └── pom.xml         # Quản lý thư viện Maven
├── bot/                # Mã nguồn Python Telegram Bot
│   ├── handlers/       # Xử lý các command & callback button
│   ├── services/       # Client kết nối API backend & Groq Vision
│   ├── main.py         # Entry point của bot
│   └── requirements.txt# Thư viện Python cần thiết
├── docker-compose.yml  # File cấu hình deploy container docker
├── .env.example        # File cấu hình môi trường mẫu
└── README.md           # Tài liệu hướng dẫn sử dụng
```
