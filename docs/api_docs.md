# TÀI LIỆU REST API - HUSTStudy Bot

Tài liệu này đặc tả toàn bộ các REST API được cung cấp bởi **Spring Boot Backend** để **Python Telegram Bot** gọi phục vụ việc tương tác, đồng bộ và quản lý dữ liệu.

> [!NOTE]
> Mọi Endpoint dưới đây có Base URL được cấu hình từ biến môi trường của Bot (mặc định là `http://localhost:8081/api`).
> Tất cả các Request và Response body đều sử dụng định dạng dữ liệu **JSON**.

---

## 1. Hệ Thống Người Dùng (User API)

Quản lý thông tin đăng ký, trạng thái hoạt động và cấu hình nhận thông báo của người dùng Telegram.

### 1.1. Đăng ký / Cập nhật người dùng
* **Endpoint**: `POST /users/register`
* **Mô tả**: Lưu thông tin người dùng mới hoặc cập nhật thông tin hiển thị nếu tài khoản đã tồn tại (gọi khi người dùng bấm `/start`).
* **Request Body**:
  ```json
  {
    "telegramId": 123456789,
    "username": "phuongdev",
    "fullName": "Phuong Dev"
  }
  ```
* **Response (201 Created)**:
  ```json
  {
    "id": 1,
    "telegramId": 123456789,
    "username": "phuongdev",
    "fullName": "Phuong Dev",
    "languageCode": "vi",
    "timezone": "Asia/Ho_Chi_Minh",
    "isActive": true
  }
  ```

### 1.2. Kiểm tra tài khoản tồn tại
* **Endpoint**: `GET /users/exists/{telegramId}`
* **Mô tả**: Kiểm tra xem người dùng đã thực hiện `/start` và đăng ký trong hệ thống chưa.
* **Response (200 OK)**: `true` hoặc `false`

### 1.3. Lấy cấu hình thông báo cá nhân
* **Endpoint**: `GET /users/{telegramId}/notifications`
* **Mô tả**: Lấy chi tiết trạng thái bật/tắt của các loại thông báo tự động (lịch học, deadline, thi, sự kiện HUST,...).
* **Response (200 OK)**:
  ```json
  {
    "notifyClassRemind": true,
    "notifyDeadline": true,
    "notifyExam": true,
    "notifyDailySummary": true,
    "notifyHustEvents": true,
    "dailySummaryTime": "07:00:00",
    "classRemindBefore": 30,
    "deadlineRemindBefore": 1440,
    "examRemindBeforeDays": 2,
    "googleSheetUrl": "https://docs.google.com/spreadsheets/d/...",
    "sheetSyncedAt": "2026-06-29T07:30:00"
  }
  ```

### 1.4. Cập nhật cài đặt thông báo
* **Endpoint**: `PATCH /users/{telegramId}/notifications`
* **Mô tả**: Thay đổi cài đặt thông báo. Chỉ những trường được gửi trong body mới được cập nhật.
* **Request Body** *(ví dụ)*:
  ```json
  {
    "notifyDailySummary": false,
    "dailySummaryTime": "06:30"
  }
  ```
* **Response (200 OK)**: Trả về Object cài đặt đầy đủ sau khi sửa (như mục 1.3).

### 1.5. Hủy kích hoạt tài khoản
* **Endpoint**: `PATCH /users/{telegramId}/deactivate`
* **Mô tả**: Đánh dấu người dùng ngừng hoạt động (`isActive = false`). Gọi khi phát hiện người dùng block/chặn bot để hệ thống ngừng gửi thông báo ngầm.
* **Response (204 No Content)**: Không có dữ liệu trả về.

### 1.6. Lấy tất cả thông tin liên lạc (Dành cho Scheduler)
* **Endpoint**: `GET /users/all-with-notifications`
* **Mô tả**: Lấy toàn bộ danh sách user đang active kèm cài đặt thông báo của họ (Dùng bởi scheduler lập lịch gửi thông báo tự động).
* **Response (200 OK)**:
  ```json
  [
    {
      "telegram_id": 123456789,
      "timezone": "Asia/Ho_Chi_Minh",
      "settings": { ... }
    }
  ]
  ```

---

## 2. Quản Lý Tài Chính & Chi Tiêu (Expense API)

Quản lý thu nhập, chi tiêu cá nhân, danh mục thu chi, đặt ngân sách và lưu trữ kết quả nhận diện hoá đơn từ AI.

### 2.1. Thêm giao dịch (Nhập tay)
* **Endpoint**: `POST /expense/add`
* **Mô tả**: Tạo một giao dịch thu nhập hoặc chi tiêu mới bằng cách nhập thủ công.
* **Request Body**:
  ```json
  {
    "telegramId": 123456789,
    "type": "EXPENSE", 
    "amount": 55000,
    "categoryName": "Ăn uống",
    "note": "Ăn sáng phở bò"
  }
  ```
* **Response (201 Created)**:
  ```json
  {
    "id": 15,
    "amount": 55000.00,
    "type": "EXPENSE",
    "categoryName": "Ăn uống",
    "note": "Ăn sáng phở bò",
    "transactionAt": "2026-06-29T07:35:00",
    "source": "MANUAL",
    "aiConfidence": null
  }
  ```

### 2.2. Xác nhận & lưu giao dịch quét bằng AI
* **Endpoint**: `POST /expense/confirm-scan`
* **Mô tả**: Lưu thông tin giao dịch nhận diện thành công từ ảnh hóa đơn (Groq Vision) sau khi người dùng nhấn nút xác nhận trên Bot.
* **Request Body**:
  ```json
  {
    "telegramId": 123456789,
    "type": "EXPENSE",
    "amount": 150000,
    "categoryName": "Mua sắm",
    "note": "Hóa đơn siêu thị Winmart",
    "imageFileId": "AgACAgQAAxkBA...",
    "aiConfidence": 0.95
  }
  ```
* **Response (201 Created)**: Tương tự response 2.1, nhưng có `source = "AI_SCAN"` và `aiConfidence = 0.95`.

### 2.3. Lấy lịch sử giao dịch
* **Endpoint**: `GET /expense/history`
* **Query Parameters**:
  * `telegramId` *(Bắt buộc)*: Số định danh Telegram.
  * `period` *(Mặc định: month)*: Khoảng thời gian lấy lịch sử (`day`, `week`, `month`, `year`).
  * `limit` *(Mặc định: 20)*: Số lượng bản ghi tối đa.
* **Response (200 OK)**: Danh sách các giao dịch (tương tự định dạng response 2.1).

### 2.4. Xem báo cáo chi tiêu tháng
* **Endpoint**: `GET /expense/report`
* **Query Parameters**:
  * `telegramId` *(Bắt buộc)*: Số định danh Telegram.
  * `month` *(Tùy chọn)*: Tháng báo cáo (1-12). Mặc định là tháng hiện tại.
  * `year` *(Tùy chọn)*: Năm báo cáo. Mặc định là năm hiện tại.
* **Response (200 OK)**:
  ```json
  {
    "totalExpense": 1250000.00,
    "totalIncome": 3000000.00,
    "netBalance": 1750000.00,
    "categorySummaries": [
      {
        "categoryName": "Ăn uống",
        "amount": 850000.00,
        "percentage": 68.0
      },
      {
        "categoryName": "Đi lại",
        "amount": 400000.00,
        "percentage": 32.0
      }
    ]
  }
  ```

### 2.5. Lấy danh sách danh mục thu/chi
* **Endpoint**: `GET /expense/categories`
* **Query Parameters**:
  * `telegramId` *(Bắt buộc)*: Trả về danh mục chung của hệ thống + các danh mục riêng do user này tạo.
* **Response (200 OK)**:
  ```json
  [
    { "id": 1, "name": "Ăn uống", "icon": "🍔", "type": "EXPENSE", "isDefault": true },
    { "id": 10, "name": "Học tập", "icon": "📚", "type": "EXPENSE", "isDefault": false }
  ]
  ```

### 2.6. Thêm danh mục riêng
* **Endpoint**: `POST /expense/categories`
* **Request Body**:
  ```json
  {
    "telegramId": 123456789,
    "name": "Nuôi mèo",
    "icon": "🐱",
    "type": "EXPENSE"
  }
  ```
* **Response (201 Created)**:
  ```json
  {
    "id": 12,
    "name": "Nuôi mèo",
    "icon": "🐱",
    "type": "EXPENSE",
    "message": "✅ Đã thêm danh mục: Nuôi mèo"
  }
  ```

### 2.7. Sửa danh mục riêng
* **Endpoint**: `PUT /expense/categories/{id}`
* **Request Body**:
  ```json
  {
    "telegramId": 123456789,
    "name": "Nuôi mèo béo",
    "icon": "🐈"
  }
  ```
* **Response (200 OK)**: Trả về thông tin danh mục sau khi sửa.

### 2.8. Xóa danh mục riêng
* **Endpoint**: `DELETE /expense/categories/{id}`
* **Query Parameters**: `telegramId` *(Bắt buộc)*
* **Response (200 OK)**:
  ```json
  {
    "message": "✅ Đã xóa danh mục"
  }
  ```

### 2.9. Cập nhật thông tin giao dịch chi tiêu
* **Endpoint**: `PUT /expense/{id}`
* **Request Body**:
  ```json
  {
    "telegramId": 123456789,
    "amount": 60000,
    "categoryName": "Ăn uống",
    "note": "Sửa thành 60k do tính thêm trà đá"
  }
  ```
* **Response (200 OK)**: Trả về thông tin giao dịch sau khi cập nhật.

### 2.10. Xóa giao dịch chi tiêu
* **Endpoint**: `DELETE /expense/{id}`
* **Query Parameters**: `telegramId` *(Bắt buộc)*
* **Response (200 OK)**:
  ```json
  {
    "message": "✅ Đã xóa giao dịch #15"
  }
  ```

### 2.11. Reset toàn bộ giao dịch chi tiêu
* **Endpoint**: `DELETE /expense/reset`
* **Query Parameters**: `telegramId` *(Bắt buộc)*
* **Response (200 OK)**:
  ```json
  {
    "message": "✅ Đã reset toàn bộ dữ liệu giao dịch chi tiêu"
  }
  ```

### 2.12. Cài đặt Groq API Key cá nhân
* **Endpoint**: `POST /expense/setkey`
* **Mô tả**: Lưu key Groq AI riêng của user để không bị tính vào giới hạn quota hàng ngày của hệ thống.
* **Request Body**:
  ```json
  {
    "telegramId": 123456789,
    "apiKey": "gsk_xxxx..."
  }
  ```
* **Response (200 OK)**:
  ```json
  {
    "message": "✅ Đã lưu API Key cá nhân của bạn thành công!"
  }
  ```

### 2.13. Xem trạng thái quota quét hóa đơn bằng AI
* **Endpoint**: `GET /expense/keystatus`
* **Query Parameters**: `telegramId` *(Bắt buộc)*
* **Response (200 OK)**:
  ```json
  {
    "hasOwnKey": false,
    "apiKey": "",
    "usedToday": 2,
    "remaining": 3,
    "isUnlimited": false,
    "freeLimit": 5,
    "message": "📊 Scan AI miễn phí: đã dùng 2/5 lượt hôm nay..."
  }
  ```

---

## 3. Lịch Học & Đồng Bộ Bảng Tính (Schedule API)

Quản lý thông tin thời khóa biểu, lịch sinh hoạt và các tác vụ đồng bộ từ Google Sheets cá nhân.

### 3.1. Lưu liên kết Google Sheet
* **Endpoint**: `POST /schedule/{telegramId}/setsheet`
* **Request Body**:
  ```json
  {
    "sheetUrl": "https://docs.google.com/spreadsheets/d/1BxiMVs0XRA/edit"
  }
  ```
* **Response (200 OK)**:
  ```json
  {
    "message": "✅ Đã lưu Google Sheet thành công!"
  }
  ```

### 3.2. Đồng bộ thời khóa biểu chính (Format 7 cột)
* **Endpoint**: `POST /schedule/{telegramId}/sync`
* **Mô tả**: Đồng bộ thời khóa biểu học tập cố định theo định dạng mẫu 7 cột cũ của trường.
* **Response (200 OK)**:
  ```json
  {
    "success": true,
    "syncedCount": 8,
    "errors": [],
    "message": "✅ Đồng bộ thành công 8 buổi học!"
  }
  ```

### 3.3. Tự động đồng bộ lịch sinh hoạt / thời gian biểu (Format 6 cột / Grid)
* **Endpoint**: `POST /schedule/{telegramId}/sync-daily`
* **Mô tả**: Đồng bộ lịch hoạt động sinh hoạt cá nhân (tự động phát hiện cấu trúc bảng theo hàng hoặc ô lưới).
* **Response (200 OK)**:
  ```json
  {
    "success": true,
    "syncedCount": 15,
    "errors": [],
    "message": "✅ Đồng bộ thành công 15 hoạt động!"
  }
  ```

### 3.4. Lấy lịch học hôm nay
* **Endpoint**: `GET /schedule/{telegramId}/today`
* **Response (200 OK)**:
  ```json
  [
    {
      "subjectName": "Cơ sở dữ liệu",
      "subjectCode": "IT3080",
      "teacher": "Nguyễn Văn A",
      "room": "B1-302",
      "startTime": "08:25",
      "endTime": "11:00",
      "dayOfWeek": 2
    }
  ]
  ```

### 3.5. Lấy lịch học cả tuần
* **Endpoint**: `GET /schedule/{telegramId}/week`
* **Response (200 OK)**: Danh sách các tiết học phân bổ theo ngày trong tuần (tương tự định dạng mục 3.4).

### 3.6. Lấy lịch sinh hoạt hôm nay
* **Endpoint**: `GET /schedule/{telegramId}/daily`
* **Query Parameters**:
  * `day` *(Tùy chọn)*: Giá trị 1 (Thứ 2) -> 7 (Chủ nhật). Mặc định là ngày hiện tại.
* **Response (200 OK)**:
  ```json
  [
    {
      "id": 102,
      "activity": "Học nhóm tự do",
      "category": "Học tập",
      "startTime": "14:00",
      "endTime": "16:30",
      "dayOfWeek": 2,
      "note": "Thư viện Tạ Quang Bửu"
    }
  ]
  ```

### 3.7. Lấy toàn bộ lịch sinh hoạt
* **Endpoint**: `GET /schedule/{telegramId}/daily/all`
* **Response (200 OK)**: Toàn bộ lịch hoạt động chi tiết (tương tự cấu trúc mục 3.6).

---

## 4. Học Từ Vựng (Vocabulary API)

Quản lý kho từ vựng tiếng Anh cá nhân áp dụng thuật toán ôn tập ngắt quãng (Spaced Repetition).

### 4.1. Thêm từ vựng mới
* **Endpoint**: `POST /vocabulary`
* **Request Body**:
  ```json
  {
    "telegramId": 123456789,
    "word": "persistent",
    "meaning": "kiên trì, bền bỉ",
    "example": "He is persistent in his pursuit of success."
  }
  ```
* **Response (201 Created)**:
  ```json
  {
    "id": 5,
    "word": "persistent",
    "meaning": "kiên trì, bền bỉ",
    "level": 0,
    "message": "✅ Đã thêm từ: persistent"
  }
  ```

### 4.2. Lấy danh sách từ đã lưu
* **Endpoint**: `GET /vocabulary/{telegramId}`
* **Response (200 OK)**:
  ```json
  [
    {
      "id": 5,
      "word": "persistent",
      "meaning": "kiên trì, bền bỉ",
      "pronunciation": "/pəˈsɪstənt/",
      "example": "He is persistent...",
      "level": 1,
      "nextReviewAt": "2026-06-30T07:30:00"
    }
  ]
  ```

### 4.3. Lấy từ tiếp theo cần ôn tập (Học / Làm Quiz)
* **Endpoint**: `GET /vocabulary/{telegramId}/next`
* **Mô tả**: Trả về 1 từ vựng có thời gian ôn tập tiếp theo (`nextReviewAt`) sớm hơn hoặc bằng thời điểm hiện tại.
* **Response (200 OK)**: Thông tin một từ vựng chi tiết cần làm quiz (tương tự như mục 4.2).
* **Response (204 No Content)**: Nếu hiện tại chưa có từ nào tới hạn cần ôn tập.

### 4.4. Nộp kết quả ôn tập (Quiz Review)
* **Endpoint**: `POST /vocabulary/{wordId}/review`
* **Mô tả**: Ghi nhận kết quả trả lời đúng/sai của người dùng để cập nhật cấp độ học (`level`) và tính toán mốc thời gian ôn tập tiếp theo (`nextReviewAt`).
* **Request Body**:
  ```json
  {
    "telegramId": 123456789,
    "correct": true
  }
  ```
* **Response (200 OK)**:
  ```json
  {
    "id": 5,
    "word": "persistent",
    "level": 2,
    "nextReviewAt": "2026-07-02T07:30:00",
    "message": "✅ Đúng! Cấp độ tăng lên Level 2"
  }
  ```

---

## 5. Quản Lý Lịch Thi (Exam API)

Lưu và cập nhật thông tin phục vụ kỳ thi học kỳ.

### 5.1. Thêm lịch thi mới
* **Endpoint**: `POST /exams`
* **Request Body**:
  ```json
  {
    "telegramId": 123456789,
    "subject": "Giải tích 1",
    "examDate": "2026-07-15",
    "startTime": "07:30",
    "room": "D3-301",
    "examType": "Trắc nghiệm"
  }
  ```
* **Response (201 Created)**:
  ```json
  {
    "id": 2,
    "subject": "Giải tích 1",
    "examDate": "2026-07-15",
    "startTime": "07:30:00",
    "room": "D3-301",
    "examType": "Trắc nghiệm",
    "message": "✅ Đã thêm lịch thi: Giải tích 1"
  }
  ```

### 5.2. Xem danh sách lịch thi
* **Endpoint**: `GET /exams/{telegramId}`
* **Response (200 OK)**: Danh sách toàn bộ các lịch thi đã được đăng ký của người dùng (tương tự cấu trúc mục 5.1).

---

## 6. Hạn Hoàn Thành Bài Tập (Deadline API)

Hệ thống theo dõi các nhiệm vụ, bài tập lớn và quản lý tiến độ.

### 6.1. Thêm mới deadline
* **Endpoint**: `POST /deadlines`
* **Request Body**:
  ```json
  {
    "telegramId": 123456789,
    "title": "Nộp báo cáo đồ án cuối kỳ",
    "dueDate": "2026-07-05",
    "subject": "Thiết kế hệ thống thông tin"
  }
  ```
* **Response (201 Created)**:
  ```json
  {
    "id": 8,
    "title": "Nộp báo cáo đồ án cuối kỳ",
    "dueDate": "2026-07-05",
    "subject": "Thiết kế hệ thống thông tin",
    "isDone": false,
    "message": "✅ Đã thêm deadline: Nộp báo cáo đồ án cuối kỳ"
  }
  ```

### 6.2. Danh sách deadline chưa hoàn thành
* **Endpoint**: `GET /deadlines/{telegramId}`
* **Mô tả**: Trả về toàn bộ danh sách các deadline ở trạng thái chưa làm (`isDone = false`).
* **Response (200 OK)**: Danh sách các bản ghi (tương tự cấu trúc mục 6.1, kèm thuộc tính `"note"` bổ sung nếu có).

### 6.3. Đánh dấu hoàn thành deadline
* **Endpoint**: `PATCH /deadlines/{id}/done`
* **Query Parameters**: `telegramId` *(Bắt buộc)*
* **Response (200 OK)**:
  ```json
  {
    "id": 8,
    "title": "Nộp báo cáo đồ án cuối kỳ",
    "isDone": true,
    "message": "✅ Đã đánh dấu xong: Nộp báo cáo đồ án cuối kỳ"
  }
  ```
