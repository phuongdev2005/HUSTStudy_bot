# Use Case Diagram — HUSTStudy Bot

## Tổng quan

Sơ đồ use case mô tả các tác nhân và ca sử dụng của hệ thống. Dựa trên danh sách lệnh đăng ký trong `bot/main.py` (`post_init`) và các handler đã/sẽ triển khai.

## Tác nhân (Actors)

| Tác nhân | Mô tả |
|---|---|
| **Người dùng (Sinh viên)** | Tương tác qua Telegram — gửi lệnh, nhận phản hồi |
| **APScheduler (Hệ thống)** | Python APScheduler chạy nền, kích hoạt thông báo định kỳ |
| **Google Sheets API** | Nhận dữ liệu xuất từ `SheetsService` (Java) |

## Sơ đồ

```plantuml
@startuml use_case_diagram
title HUSTStudy Bot — Use Case Diagram

skinparam ActorStyle awesome
skinparam usecase {
    BackgroundColor LightBlue
    BorderColor DarkBlue
    ArrowColor DarkBlue
}
skinparam rectangle {
    BackgroundColor WhiteSmoke
    BorderColor DarkGray
}

left to right direction

actor "Người dùng\n(Sinh viên)" as User
actor "APScheduler\n(Hệ thống)" as Scheduler
actor "Google Sheets API" as GSheets

rectangle "HUSTStudy Bot" {

    rectangle "Tài khoản" {
        usecase "Đăng ký / Cập nhật\n(/start) ✅" as UC01
        usecase "Xem hướng dẫn\n(/help)" as UC02
    }

    rectangle "Thời khóa biểu" {
        usecase "Xem TKB hôm nay\n(/schedule)" as UC03
        usecase "Thêm môn học" as UC04
        usecase "Xóa môn học" as UC05
    }

    rectangle "Deadline & Lịch thi" {
        usecase "Xem deadline\n(/deadline)" as UC06
        usecase "Thêm deadline" as UC07
        usecase "Đánh dấu hoàn thành" as UC08
        usecase "Xem lịch thi\n(/exam)" as UC09
        usecase "Thêm lịch thi" as UC10
    }

    rectangle "Chi tiêu cá nhân" {
        usecase "Ghi chi tiêu\n(/addexpense)" as UC11
        usecase "Ghi thu nhập\n(/addincome)" as UC12
        usecase "Xem báo cáo\n(/report)" as UC13
        usecase "Đặt ngân sách" as UC14
    }

    rectangle "Từ vựng tiếng Anh" {
        usecase "Ôn tập (quiz)\n(/quiz)" as UC15
        usecase "Thêm từ vựng" as UC16
    }

    rectangle "Xuất dữ liệu" {
        usecase "Xuất TKB ra Sheets" as UC17
        usecase "Xuất chi tiêu ra Sheets" as UC18
        usecase "Xuất toàn bộ" as UC19
    }

    rectangle "Thông báo tự động" {
        usecase "Nhắc giờ học" as UC20
        usecase "Nhắc deadline" as UC21
        usecase "Nhắc lịch thi" as UC22
        usecase "Tổng hợp sự kiện ngày" as UC23
        usecase "Cảnh báo ngân sách" as UC24
    }
}

User --> UC01
User --> UC02
User --> UC03
User --> UC04
User --> UC05
User --> UC06
User --> UC07
User --> UC08
User --> UC09
User --> UC10
User --> UC11
User --> UC12
User --> UC13
User --> UC14
User --> UC15
User --> UC16
User --> UC17
User --> UC18
User --> UC19

Scheduler --> UC20
Scheduler --> UC21
Scheduler --> UC22
Scheduler --> UC23
Scheduler --> UC24

UC17 --> GSheets
UC18 --> GSheets
UC19 --> GSheets

@enduml
```

## Trạng thái triển khai

### ✅ Đã triển khai
| Use Case | Lệnh | File |
|---|---|---|
| UC01 — Đăng ký/Cập nhật | `/start` | `bot/handlers/start.py` + `UserController.java` |

### 📋 Đã đăng ký trong menu Telegram (main.py)
Các lệnh sau được đăng ký trong `post_init()` nhưng **chưa có handler**:

| Lệnh | Mô tả |
|---|---|
| `/schedule` | Xem thời khóa biểu hôm nay |
| `/deadline` | Xem deadline sắp tới |
| `/exam` | Xem lịch thi |
| `/addexpense` | Ghi chi tiêu |
| `/addincome` | Ghi thu nhập |
| `/report` | Báo cáo chi tiêu tháng này |
| `/quiz` | Ôn từ vựng tiếng Anh |
| `/help` | Hướng dẫn sử dụng |

### 🔲 Chưa triển khai
- Tất cả chức năng thêm/sửa/xóa dữ liệu (thêm môn, thêm deadline, thêm lịch thi, thêm từ vựng).
- Xuất dữ liệu ra Google Sheets (`SheetsService` mới là stub).
- APScheduler — chưa setup bất kỳ job nào.
- Cảnh báo ngân sách (logic đã thiết kế trong `budgets`, chưa có scheduler gọi).

## Mô tả nhóm chức năng

### 1. Tài khoản
- **UC01 — /start**: Gọi `POST /api/users/register` → tạo mới hoặc cập nhật user. Tạo đồng thời `user_settings` với giá trị mặc định.

### 2. Thời khóa biểu
- Quản lý bảng `subjects` và `class_schedules`. `day_of_week` dùng convention 1=Thứ2...7=CN.
- View `v_today_schedule` hỗ trợ query nhanh lịch hôm nay.

### 3. Deadline & Lịch thi
- `deadlines` có `priority` (LOW/MEDIUM/HIGH) và `status` (PENDING/DONE/OVERDUE).
- `exams` lưu `subject_name` riêng để không mất dữ liệu khi xóa môn.
- Cả hai có `is_notified` để tránh gửi thông báo trùng.

### 4. Chi tiêu cá nhân
- `expenses` → `expense_categories` (có 10 danh mục mặc định seeded).
- `budgets` có `warn_threshold` (default 0.80) và 2 cờ `is_notified_80/100`.
- View `v_budget_status` và `v_monthly_expense_summary` hỗ trợ báo cáo.

### 5. Từ vựng tiếng Anh
- Bảng `vocabularies` dùng **thuật toán SM-2** (Spaced Repetition): `review_interval`, `ease_factor`.
- `vocab_sessions` → nhiều `vocab_answers` (tách biệt session header và chi tiết từng câu).

### 6. Thông báo tự động (APScheduler)
- **UC20**: Đọc `class_schedules` + `user_settings.notify_class_remind` + `class_remind_before`.
- **UC21**: Đọc `deadlines` WHERE `status='PENDING'` + `notify_deadline`.
- **UC22**: Đọc `exams` + `notify_exam` + `remind_days`.
- **UC23**: Tổng hợp sự kiện ngày lúc `daily_summary_time` (default 07:00).
- **UC24**: Đọc view `v_budget_status`, gửi khi `spent_pct >= warn_threshold AND is_notified_80=0`.
- Mọi thông báo đã gửi được ghi vào `notification_logs`.
