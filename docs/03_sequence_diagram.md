# Sequence Diagram — HUSTStudy Bot

## Tổng quan

Sơ đồ tuần tự mô tả tương tác giữa các thành phần theo thứ tự thời gian. Dựa trên source code thực tế: `bot/handlers/start.py`, `bot/services/api_client.py`, và `backend/.../UserController.java`.

**Base URL API:** `http://localhost:8081/api` (cấu hình trong `bot/config.py` qua `API_BASE_URL`)

---

## Sequence 1 — Đăng ký người dùng (/start)

### Đã triển khai trong code

- `bot/handlers/start.py` → `start_handler()`
- `bot/services/api_client.py` → `register_user()`
- `backend/.../UserController.java` → `POST /users/register`

```plantuml
@startuml sequence_start
title Sequence Diagram — Đăng ký người dùng (/start)

skinparam SequenceArrowThickness 2
skinparam SequenceBoxBackgroundColor LightBlue
skinparam ParticipantBackgroundColor WhiteSmoke
skinparam ParticipantBorderColor DarkBlue
skinparam NoteBackgroundColor LightYellow

actor       "Người dùng"        as User
participant "Telegram API"      as TG
participant "Python Bot\n(handlers/start.py)" as Bot
participant "ApiClient\n(services/api_client.py)" as Client
participant "Java API\n(POST /users/register)" as API
database    "MySQL"             as DB

User -> TG  : Gõ /start
TG   -> Bot : Update { message: "/start" }

Bot  -> Bot : user = update.effective_user\n(id, username, full_name)

Bot  -> Client : register_user(\n  telegram_id=user.id,\n  username=user.username or "",\n  full_name=user.full_name)

Client -> API : POST /api/users/register\nJSON { telegramId, username, fullName }
note right : httpx.AsyncClient\ntimeout = 10s

API  -> DB  : SELECT * FROM users\nWHERE telegram_id = ?
DB  --> API : result

alt user chưa tồn tại
    API  -> DB  : INSERT INTO users (...)\n+ INSERT INTO user_settings (...)
    note right : UserSettings defaults:\nnotify_* = true\nclassRemindBefore = 30\ndeadlineRemindBefore = 1440\nexamRemindBeforeDays = 2
    DB  --> API : user_id = N
    API --> Client : HTTP 201 Created\n{ id, telegramId, username,\n  fullName, languageCode,\n  timezone, isActive, createdAt }
else user đã tồn tại
    API  -> DB  : UPDATE users SET\n  full_name=?, username=?, is_active=1\nWHERE telegram_id=?
    DB  --> API : ok
    API --> Client : HTTP 201 Created\n{ id, telegramId, ... }
end

Client --> Bot : dict (JSON response)

Bot  -> TG  : reply_text(\n  "👋 Xin chào *{first_name}*!\n  🤖 Mình là HUSTStudy Bot...\n  • /schedule • /deadline\n  • /exam • /addexpense\n  • /report • /quiz",\n  parse_mode="Markdown")

TG   -> User : Tin nhắn chào + danh sách lệnh

@enduml
```

### Ghi chú
- Python Bot dùng `httpx.AsyncClient` với `base_url = API_BASE_URL` và `timeout = 10.0` giây.
- `response.raise_for_status()` được gọi → nếu API trả lỗi HTTP ≥ 400, exception sẽ bubble up.
- API luôn trả `201 Created` cho cả create và update (thiết kế hiện tại).
- `UserResponse` bao gồm: `id`, `telegramId`, `username`, `fullName`, `languageCode`, `timezone`, `isActive`, `createdAt`.

---

## Sequence 2 — Ghi chi tiêu (/addexpense)

### Trạng thái: Thiết kế (handler chưa implement)

Endpoint Java cần tạo: `POST /api/expenses`

```plantuml
@startuml sequence_addexpense
title Sequence Diagram — Ghi chi tiêu (/addexpense)

skinparam SequenceArrowThickness 2
skinparam ParticipantBackgroundColor WhiteSmoke
skinparam ParticipantBorderColor DarkOrange

actor       "Người dùng"    as User
participant "Telegram API"  as TG
participant "Python Bot"    as Bot
participant "Java API\n(:8081)" as API
database    "MySQL"         as DB

User -> TG  : /addexpense 35000 cơm trưa
TG   -> Bot : Update { message: "/addexpense 35000 cơm trưa" }
Bot  -> Bot : parse: amount=35000, note="cơm trưa"

Bot  -> TG  : sendMessage(\n  InlineKeyboardMarkup\n  [🍜 Ăn uống] [🚌 Di chuyển]\n  [📚 Học phí] [🎮 Giải trí])
TG   -> User : Keyboard chọn danh mục

User -> TG  : Tap "🍜 Ăn uống"
TG   -> Bot : CallbackQuery { data: "cat_1" }

Bot  -> API : POST /api/expenses\n{ telegramId, categoryId:1,\n  type:"EXPENSE", amount:35000,\n  note:"cơm trưa" }

API  -> DB  : INSERT INTO expenses\n(user_id, category_id, type,\n amount, note, transaction_at)
DB  --> API : expense_id = N

API  -> DB  : SELECT SUM(amount) FROM expenses\nWHERE user_id=? AND category_id=1\nAND type='EXPENSE'\nAND MONTH(transaction_at)=MONTH(NOW())
DB  --> API : spent = 850000

API  -> DB  : SELECT amount, warn_threshold,\n  is_notified_80\nFROM budgets\nWHERE user_id=? AND category_id=1\nAND month=? AND year=?
DB  --> API : amount=1000000, threshold=0.80, is_notified_80=0

API  -> API : pct = 850000/1000000 = 0.85\n0.85 >= 0.80 AND is_notified_80=0

alt pct >= warn_threshold AND NOT is_notified_80
    API  -> DB  : UPDATE budgets SET is_notified_80=1\nWHERE ...
    API --> Bot : 201 { expenseId, spentAmount:850000,\n  budgetAmount:1000000, spentPct:85.0,\n  warned:true }
    Bot  -> TG  : "✅ Đã ghi: -35,000đ | 🍜 Ăn uống | cơm trưa\n⚠️ Đã dùng 85% ngân sách tháng này!"
else pct < warn_threshold
    API --> Bot : 201 { expenseId, spentPct:50.0, warned:false }
    Bot  -> TG  : "✅ Đã ghi: -35,000đ | 🍜 Ăn uống | cơm trưa"
end

TG   -> User : Xác nhận

@enduml
```

### Ghi chú
- `category_id` là INT (bảng `expense_categories` dùng `INT`, không phải `BIGINT`).
- `warn_threshold` default `0.80` — lấy từ cột trong `budgets`, không hardcode.
- Cờ `is_notified_80` ngăn gửi cảnh báo lặp lại trong cùng tháng.
- Bot lưu `amount` và `note` tạm trong `context.user_data` giữa 2 bước (lệnh → callback).

---

## Sequence 3 — Scheduler nhắc giờ học (tự động)

### Trạng thái: Thiết kế (APScheduler chưa implement)

Endpoint Java cần tạo: `GET /api/schedule/upcoming`

```plantuml
@startuml sequence_scheduler
title Sequence Diagram — Scheduler nhắc giờ học (tự động)

skinparam SequenceArrowThickness 2
skinparam ParticipantBackgroundColor WhiteSmoke
skinparam ParticipantBorderColor DarkGreen

participant "APScheduler\n(Python)" as SC
participant "Java API\n(:8081)" as API
database    "MySQL"             as DB
participant "Python Bot"        as Bot
participant "Telegram API"      as TG
actor       "Người dùng"        as User

== Mỗi phút: job check_class_reminders ==

SC   -> API : GET /api/schedule/upcoming?minutesAhead=30
API  -> DB  : SELECT u.telegram_id,\n  s.name AS subject_name,\n  COALESCE(cs.room, s.room) AS room,\n  cs.start_time, cs.end_time\nFROM class_schedules cs\nJOIN subjects s ON s.id = cs.subject_id\nJOIN users u ON u.id = cs.user_id\nJOIN user_settings us ON us.user_id = u.id\nWHERE cs.is_active = 1 AND s.is_active = 1\nAND cs.day_of_week = DAYOFWEEK(CURDATE()) - 1\nAND TIME(cs.start_time) BETWEEN TIME(NOW())\n  AND ADDTIME(TIME(NOW()), SEC_TO_TIME(30*60))\nAND us.notify_class_remind = 1

note right : day_of_week: 1=T2...7=CN\nvs DAYOFWEEK(): 1=CN...7=T7\nnên offset -1

DB  --> API : [{ telegramId, subjectName, room,\n   startTime, endTime }]
API --> SC  : List<ReminderDTO>

loop Mỗi reminder (sleep 50ms chống Telegram flood)
    SC   -> Bot  : send_message(\n  chat_id=telegramId,\n  text="⏰ Nhắc lịch học\n🏫 {subjectName} lúc {startTime}\n📍 Phòng {room}")
    Bot  -> TG   : sendMessage(chat_id, text)
    TG   -> User : Thông báo push
end

@enduml
```

### Ghi chú
- `class_schedules.day_of_week`: 1=Thứ2, ..., 7=CN (quy ước riêng của dự án).
- MySQL `DAYOFWEEK()` trả 1=CN, 2=Thứ2, ..., 7=Thứ7 → phải offset `-1` khi query.
- Dùng view `v_today_schedule` đã có trong DB sẽ đơn giản hơn (view đã xử lý `DAYOFWEEK(CURDATE()) - 1`).
- Delay 50ms giữa các `sendMessage` để tránh vượt rate limit Telegram (30 msg/giây).
- Tương tự cho các scheduler khác: deadline (`notify_deadline`), exam (`notify_exam`), daily summary (`notify_daily_summary`).

---

## Tóm tắt endpoints đã implement

| Endpoint | Method | Handler Python | Controller Java | Trạng thái |
|---|---|---|---|---|
| `/api/users/register` | POST | `api_client.register_user()` | `UserController.register()` | ✅ Done |
| `/api/users/telegram/{id}` | GET | `api_client.get_user()` | `UserController.getByTelegramId()` | ✅ Done |
| `/api/users/exists/{id}` | GET | `api_client.user_exists()` | `UserController.exists()` | ✅ Done |
| `/api/expenses` | POST | — | — | 🔲 TODO |
| `/api/schedule/upcoming` | GET | — | — | 🔲 TODO |
| `/api/export/*` | POST | — | `SheetsService` (stub) | 🔲 TODO |
