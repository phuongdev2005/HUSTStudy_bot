# 📖 Tài liệu thiết kế — HUSTStudy Bot

## Danh sách tài liệu

| # | Tài liệu | Mô tả |
|---|---|---|
| 1 | [Use Case Diagram](./01_use_case_diagram.md) | Các tác nhân và ca sử dụng của hệ thống |
| 2 | [Activity Diagram](./02_activity_diagram.md) | Luồng hoạt động của các chức năng chính |
| 3 | [Sequence Diagram](./03_sequence_diagram.md) | Tương tác giữa các thành phần theo thời gian |
| 4 | [Class Diagram](./04_class_diagram.md) | Cấu trúc class Java Backend và Python Bot |
| 5 | [ERD](./05_erd.md) | Sơ đồ quan hệ thực thể toàn bộ database |

---

## Kiến trúc tổng quan

```
Người dùng Telegram
        │
        ▼
Telegram Bot API
        │
   ┌────┴────┐
   ▼         ▼
Python Bot  Java Backend (Spring Boot)
(handlers)  (REST API :8081)
   │              │
   │         ┌────┴────┐
   │         ▼         ▼
   └──── MySQL DB   Google Sheets API
```

## Stack công nghệ

| Thành phần | Công nghệ |
|---|---|
| Telegram Bot | Python 3.11, python-telegram-bot |
| Scheduler | APScheduler |
| Backend API | Java 17, Spring Boot 3.3 |
| ORM | Spring Data JPA + Hibernate |
| Database Migration | Flyway |
| Database | MySQL 8.0 |
| Export | Google Sheets API v4 |
| Container | Docker + Docker Compose |
