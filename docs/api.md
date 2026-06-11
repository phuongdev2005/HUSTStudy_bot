# API Documentation — HUSTStudy Bot Backend

**Base URL:** `http://localhost:8081/api`
**Content-Type:** `application/json`
**Encoding:** `UTF-8`

---

## Quy uoc chung

### HTTP Status Codes

| Code | Y nghia |
|---|---|
| `200 OK` | Thanh cong (GET, PUT) |
| `201 Created` | Tao moi thanh cong (POST) |
| `204 No Content` | Xoa thanh cong (DELETE) |
| `400 Bad Request` | Du lieu dau vao khong hop le |
| `404 Not Found` | Khong tim thay resource |
| `500 Internal Server Error` | Loi server |

### Cau truc loi

```json
{
  "timestamp": "2025-06-11T07:30:00",
  "status": 400,
  "error": "Bad Request",
  "message": "fullName khong duoc de trong",
  "path": "/api/users/register"
}
```

---

## 1. User API

### POST `/users/register`
Dang ky user moi hoac cap nhat neu da ton tai. Goi khi user dung lenh `/start`.

**Request Body:**
```json
{
  "telegramId": 123456789,
  "username": "phuongdev",
  "fullName": "Phuong Dev",
  "languageCode": "vi",
  "timezone": "Asia/Ho_Chi_Minh"
}
```

| Field | Type | Required | Mo ta |
|---|---|---|---|
| `telegramId` | Long | Yes | Telegram chat_id |
| `username` | String | No | @username Telegram |
| `fullName` | String | Yes | Ten hien thi |
| `languageCode` | String | No | Mac dinh: `vi` |
| `timezone` | String | No | Mac dinh: `Asia/Ho_Chi_Minh` |

**Response `201 Created`:**
```json
{
  "id": 1,
  "telegramId": 123456789,
  "username": "phuongdev",
  "fullName": "Phuong Dev",
  "languageCode": "vi",
  "timezone": "Asia/Ho_Chi_Minh",
  "isActive": true,
  "createdAt": "2025-06-11T07:00:00"
}
```

---

### GET `/users/telegram/{telegramId}`
Lay thong tin user theo Telegram ID.

**Path Parameter:** `telegramId` — Telegram chat_id

**Response `200 OK`:**
```json
{
  "id": 1,
  "telegramId": 123456789,
  "fullName": "Phuong Dev",
  "isActive": true,
  "createdAt": "2025-06-11T07:00:00"
}
```

**Response `404 Not Found`:**
```json
{
  "message": "Khong tim thay user voi telegramId: 123456789"
}
```

---

### GET `/users/exists/{telegramId}`
Kiem tra user da dang ky chua.

**Response `200 OK`:**
```json
true
```

---

## 2. Schedule API

### POST `/schedule/subjects`
Them mon hoc moi.

**Request Body:**
```json
{
  "telegramId": 123456789,
  "name": "Java Programming",
  "code": "IT3080",
  "teacher": "Nguyen Van A",
  "credits": 3
}
```

**Response `201 Created`:**
```json
{
  "id": 1,
  "name": "Java Programming",
  "code": "IT3080",
  "teacher": "Nguyen Van A",
  "credits": 3,
  "isActive": true,
  "sessions": []
}
```

---

### POST `/schedule/subjects/{subjectId}/sessions`
Them buoi hoc cho mot mon.

**Request Body:**
```json
{
  "dayOfWeek": 2,
  "startTime": "07:00",
  "endTime": "09:30",
  "room": "B1-301",
  "weekType": "ALL"
}
```

| Field | Type | Mo ta |
|---|---|---|
| `dayOfWeek` | Integer | 2=Thu 2, 3=Thu 3, ..., 8=Chu nhat |
| `startTime` | String | Dinh dang `HH:mm` |
| `endTime` | String | Dinh dang `HH:mm` |
| `room` | String | Phong hoc |
| `weekType` | String | `ALL` / `EVEN` / `ODD` |

---

### GET `/schedule/today?telegramId={telegramId}`
Lay lich hoc hom nay cua user.

**Response `200 OK`:**
```json
[
  {
    "subjectId": 1,
    "subjectName": "Java Programming",
    "startTime": "07:00",
    "endTime": "09:30",
    "room": "B1-301",
    "dayOfWeek": 2,
    "weekType": "ALL"
  }
]
```

---

### GET `/schedule/week?telegramId={telegramId}`
Lay toan bo thoi khoa bieu theo tuan.

**Response `200 OK`:**
```json
{
  "2": [
    { "subjectName": "Java Programming", "startTime": "07:00", "room": "B1-301" }
  ],
  "4": [
    { "subjectName": "Cau truc du lieu", "startTime": "13:00", "room": "D3-201" }
  ]
}
```

---

### GET `/schedule/upcoming?minutesAhead={minutes}`
Lay cac buoi hoc sap bat dau (dung cho Scheduler nhac gio hoc).

**Query Params:** `minutesAhead` — so phut nhin truoc (mac dinh: 30)

**Response `200 OK`:**
```json
[
  {
    "telegramId": 123456789,
    "subjectName": "Java Programming",
    "startTime": "07:00",
    "room": "B1-301"
  }
]
```

---

### DELETE `/schedule/subjects/{subjectId}`
Xoa mon hoc va tat ca buoi hoc lien quan.

**Response `204 No Content`**

---

## 3. Deadline API

### POST `/deadlines`
Them deadline moi.

**Request Body:**
```json
{
  "telegramId": 123456789,
  "title": "Bao cao mon Linux",
  "subject": "He dieu hanh Linux",
  "dueDate": "2025-06-15",
  "note": "Nop qua portal"
}
```

**Response `201 Created`:**
```json
{
  "id": 1,
  "title": "Bao cao mon Linux",
  "subject": "He dieu hanh Linux",
  "dueDate": "2025-06-15",
  "isDone": false,
  "daysLeft": 4,
  "createdAt": "2025-06-11T07:00:00"
}
```

---

### GET `/deadlines?telegramId={telegramId}&onlyPending={bool}`
Lay danh sach deadline.

**Query Params:**

| Param | Type | Default | Mo ta |
|---|---|---|---|
| `telegramId` | Long | — | Bat buoc |
| `onlyPending` | Boolean | `true` | Chi lay chua hoan thanh |
| `daysAhead` | Integer | `7` | Loc trong N ngay toi |

**Response `200 OK`:**
```json
[
  {
    "id": 1,
    "title": "Bao cao mon Linux",
    "dueDate": "2025-06-15",
    "isDone": false,
    "daysLeft": 4
  }
]
```

---

### PATCH `/deadlines/{id}/done`
Danh dau deadline da hoan thanh.

**Response `200 OK`:**
```json
{
  "id": 1,
  "isDone": true
}
```

---

### DELETE `/deadlines/{id}`
Xoa deadline.

**Response `204 No Content`**

---

## 4. Exam API

### POST `/exams`
Them lich thi.

**Request Body:**
```json
{
  "telegramId": 123456789,
  "subject": "Cau truc du lieu",
  "examDate": "2025-06-20",
  "startTime": "07:00",
  "durationMinutes": 90,
  "room": "A305",
  "examType": "Tu luan",
  "note": "Duoc mang tai lieu"
}
```

**Response `201 Created`:**
```json
{
  "id": 1,
  "subject": "Cau truc du lieu",
  "examDate": "2025-06-20",
  "startTime": "07:00",
  "durationMinutes": 90,
  "room": "A305",
  "examType": "Tu luan",
  "daysLeft": 9
}
```

---

### GET `/exams?telegramId={telegramId}`
Lay danh sach lich thi sap toi.

**Response `200 OK`:**
```json
[
  {
    "id": 1,
    "subject": "Cau truc du lieu",
    "examDate": "2025-06-20",
    "startTime": "07:00",
    "room": "A305",
    "daysLeft": 9
  }
]
```

---

### GET `/exams/upcoming?daysAhead={days}`
Lay cac ky thi sap dien ra (dung cho Scheduler nhac lich thi).

**Response `200 OK`:**
```json
[
  {
    "telegramId": 123456789,
    "subject": "Cau truc du lieu",
    "examDate": "2025-06-20",
    "startTime": "07:00",
    "room": "A305",
    "daysLeft": 2
  }
]
```

---

### DELETE `/exams/{id}`
Xoa lich thi.

**Response `204 No Content`**

---

## 5. Expense API

### POST `/expense/transactions`
Ghi giao dich thu/chi.

**Request Body:**
```json
{
  "telegramId": 123456789,
  "type": "EXPENSE",
  "amount": 35000,
  "categoryId": 1,
  "note": "com trua",
  "transactedAt": "2025-06-11T12:00:00"
}
```

| Field | Type | Required | Mo ta |
|---|---|---|---|
| `type` | String | Yes | `EXPENSE` hoac `INCOME` |
| `amount` | Long | Yes | So tien (VND) |
| `categoryId` | Long | No | ID danh muc |
| `note` | String | No | Ghi chu |
| `transactedAt` | DateTime | No | Mac dinh: thoi diem hien tai |

**Response `201 Created`:**
```json
{
  "id": 42,
  "type": "EXPENSE",
  "amount": 35000,
  "category": { "id": 1, "name": "An uong" },
  "note": "com trua",
  "transactedAt": "2025-06-11T12:00:00",
  "budgetStatus": {
    "categoryName": "An uong",
    "used": 850000,
    "limit": 1000000,
    "percentage": 85,
    "warning": true
  }
}
```

---

### GET `/expense/transactions?telegramId={id}&period={period}`
Lay lich su giao dich.

**Query Params:**

| Param | Gia tri | Mo ta |
|---|---|---|
| `period` | `today` / `week` / `month` | Khoang thoi gian |
| `type` | `EXPENSE` / `INCOME` / `ALL` | Loc loai giao dich |

---

### GET `/expense/report?telegramId={id}&month={m}&year={y}`
Lay bao cao chi tieu theo thang.

**Response `200 OK`:**
```json
{
  "month": 6,
  "year": 2025,
  "totalExpense": 1545000,
  "totalIncome": 3000000,
  "remaining": 1455000,
  "categories": [
    {
      "id": 1,
      "name": "An uong",
      "amount": 850000,
      "limit": 1000000,
      "percentage": 85
    },
    {
      "id": 2,
      "name": "Di chuyen",
      "amount": 120000,
      "limit": 300000,
      "percentage": 40
    }
  ]
}
```

---

### GET `/expense/categories`
Lay danh sach tat ca danh muc chi tieu.

**Response `200 OK`:**
```json
[
  { "id": 1, "name": "An uong",       "isDefault": true },
  { "id": 2, "name": "Di chuyen",     "isDefault": true },
  { "id": 3, "name": "Hoc phi & Sach","isDefault": true },
  { "id": 4, "name": "Giai tri",      "isDefault": true },
  { "id": 5, "name": "Mua sam",       "isDefault": true },
  { "id": 6, "name": "Y te",          "isDefault": true },
  { "id": 7, "name": "Khac",          "isDefault": true }
]
```

---

### POST `/expense/budgets`
Dat ngan sach cho mot danh muc trong thang.

**Request Body:**
```json
{
  "telegramId": 123456789,
  "categoryId": 1,
  "limitAmount": 1000000,
  "month": 6,
  "year": 2025
}
```

**Response `201 Created`:**
```json
{
  "id": 1,
  "category": { "id": 1, "name": "An uong" },
  "limitAmount": 1000000,
  "month": 6,
  "year": 2025
}
```

---

### GET `/expense/budgets?telegramId={id}&month={m}&year={y}`
Lay trang thai ngan sach thang.

**Response `200 OK`:**
```json
[
  {
    "category": { "name": "An uong" },
    "limitAmount": 1000000,
    "usedAmount": 850000,
    "percentage": 85,
    "warning": true
  }
]
```

---

## 6. Vocabulary API

### POST `/vocabulary/words`
Them tu vung moi.

**Request Body:**
```json
{
  "telegramId": 123456789,
  "word": "computer",
  "meaning": "may tinh",
  "example": "I use a computer every day.",
  "pronunciation": "/kompjuter/"
}
```

**Response `201 Created`:**
```json
{
  "id": 1,
  "word": "computer",
  "meaning": "may tinh",
  "example": "I use a computer every day.",
  "pronunciation": "/kompjuter/",
  "level": 0,
  "nextReviewAt": "2025-06-11T07:00:00"
}
```

---

### GET `/vocabulary/words?telegramId={id}&dueOnly={bool}`
Lay danh sach tu vung.

**Query Params:**

| Param | Default | Mo ta |
|---|---|---|
| `dueOnly` | `false` | `true` = chi lay tu can on hom nay |
| `limit` | `20` | So tu toi da |

**Response `200 OK`:**
```json
[
  {
    "id": 1,
    "word": "computer",
    "meaning": "may tinh",
    "level": 0,
    "nextReviewAt": "2025-06-11T07:00:00"
  }
]
```

---

### POST `/vocabulary/quiz-results`
Luu ket qua phien on tap va cap nhat level tung tu.

**Request Body:**
```json
{
  "telegramId": 123456789,
  "totalQuestions": 10,
  "correctAnswers": 8,
  "wrongAnswers": 2,
  "wordResults": [
    { "wordId": 1, "correct": true },
    { "wordId": 2, "correct": false }
  ]
}
```

**Response `201 Created`:**
```json
{
  "id": 5,
  "totalQuestions": 10,
  "correctAnswers": 8,
  "wrongAnswers": 2,
  "scorePercent": 80,
  "playedAt": "2025-06-11T08:00:00"
}
```

---

### DELETE `/vocabulary/words/{id}`
Xoa tu vung.

**Response `204 No Content`**

---

## 7. Export API

### POST `/export/schedule`
Xuat thoi khoa bieu ra Google Sheets.

**Request Body:**
```json
{
  "telegramId": 123456789,
  "sheetId": "1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgVE2upms"
}
```

**Response `200 OK`:**
```json
{
  "success": true,
  "sheetUrl": "https://docs.google.com/spreadsheets/d/1BxiMV.../edit",
  "sheetName": "Lich hoc",
  "updatedRows": 15
}
```

---

### POST `/export/expense`
Xuat bao cao chi tieu ra Google Sheets.

**Request Body:**
```json
{
  "telegramId": 123456789,
  "sheetId": "1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgVE2upms",
  "month": 6,
  "year": 2025
}
```

**Response `200 OK`:**
```json
{
  "success": true,
  "sheetUrl": "https://docs.google.com/spreadsheets/d/1BxiMV.../edit",
  "sheetName": "Chi tieu T6/2025",
  "updatedRows": 42
}
```

---

### POST `/export/all`
Xuat toan bo du lieu ra Google Sheets.

**Request Body:**
```json
{
  "telegramId": 123456789,
  "sheetId": "1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgVE2upms"
}
```

**Response `200 OK`:**
```json
{
  "success": true,
  "sheetUrl": "https://docs.google.com/spreadsheets/d/1BxiMV.../edit",
  "exportedSheets": ["Lich hoc", "Deadline & Thi", "Chi tieu T6/2025"]
}
```

---

## 8. Notification API (Internal — Scheduler only)

### GET `/notifications/class-reminders?minutesAhead={n}`
Lay danh sach nhac gio hoc (goi noi bo tu Scheduler).

### GET `/notifications/deadline-reminders`
Lay danh sach nhac deadline sap toi.

### GET `/notifications/exam-reminders?daysAhead={n}`
Lay danh sach nhac lich thi.

### GET `/notifications/daily-summary`
Lay du lieu tong hop ngay cho tat ca user (goi luc 07:00 hang ngay).

---

## Phu luc — Bang tong hop Endpoints

| Module | Method | Endpoint | Mo ta |
|---|---|---|---|
| User | POST | `/users/register` | Dang ky / cap nhat user |
| User | GET | `/users/telegram/{id}` | Lay thong tin user |
| User | GET | `/users/exists/{id}` | Kiem tra user ton tai |
| Schedule | POST | `/schedule/subjects` | Them mon hoc |
| Schedule | POST | `/schedule/subjects/{id}/sessions` | Them buoi hoc |
| Schedule | GET | `/schedule/today` | Lich hoc hom nay |
| Schedule | GET | `/schedule/week` | Lich hoc ca tuan |
| Schedule | GET | `/schedule/upcoming` | Buoi hoc sap toi (Scheduler) |
| Schedule | DELETE | `/schedule/subjects/{id}` | Xoa mon hoc |
| Deadline | POST | `/deadlines` | Them deadline |
| Deadline | GET | `/deadlines` | Danh sach deadline |
| Deadline | PATCH | `/deadlines/{id}/done` | Danh dau hoan thanh |
| Deadline | DELETE | `/deadlines/{id}` | Xoa deadline |
| Exam | POST | `/exams` | Them lich thi |
| Exam | GET | `/exams` | Danh sach lich thi |
| Exam | GET | `/exams/upcoming` | Lich thi sap toi (Scheduler) |
| Exam | DELETE | `/exams/{id}` | Xoa lich thi |
| Expense | POST | `/expense/transactions` | Ghi giao dich |
| Expense | GET | `/expense/transactions` | Lich su giao dich |
| Expense | GET | `/expense/report` | Bao cao thang |
| Expense | GET | `/expense/categories` | Danh sach danh muc |
| Expense | POST | `/expense/budgets` | Dat ngan sach |
| Expense | GET | `/expense/budgets` | Trang thai ngan sach |
| Vocabulary | POST | `/vocabulary/words` | Them tu vung |
| Vocabulary | GET | `/vocabulary/words` | Danh sach tu vung |
| Vocabulary | POST | `/vocabulary/quiz-results` | Luu ket qua quiz |
| Vocabulary | DELETE | `/vocabulary/words/{id}` | Xoa tu vung |
| Export | POST | `/export/schedule` | Xuat TKB ra Sheets |
| Export | POST | `/export/expense` | Xuat chi tieu ra Sheets |
| Export | POST | `/export/all` | Xuat toan bo |
