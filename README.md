# 📚 BÁO CÁO ĐỀ TÀI: BOT TELEGRAM QUẢN LÝ HỌC TẬP & CHI TIÊU

---

## 1. Đề bài

Trong quá trình học tập, học sinh và sinh viên thường gặp nhiều khó khăn như:

- Quên lịch học.
- Quên deadline bài tập.
- Không theo dõi được lịch thi.
- Khó quản lý thời khóa biểu cá nhân.
- Thiếu công cụ hỗ trợ ôn tập từ vựng.
- **Chi tiêu không kiểm soát**, không biết tiền đi đâu cuối tháng.
- Không có cái nhìn tổng quan về tài chính cá nhân.

Để giải quyết các vấn đề trên, đề tài xây dựng một **bot Telegram quản lý học tập và chi tiêu** nhằm hỗ trợ người dùng tổ chức lịch học, theo dõi nhiệm vụ, ôn tập hiệu quả và kiểm soát tài chính cá nhân ngay trong ứng dụng Telegram.

Bot dự kiến cung cấp các nhóm chức năng chính:

- Quản lý thời khóa biểu.
- Nhắc lịch học, deadline bài tập và lịch thi.
- Thông báo các sự kiện học tập trong ngày.
- Xuất dữ liệu và báo cáo lên Google Sheets.
- Hỏi đáp và ôn tập từ vựng tiếng Anh.
- **Quản lý chi tiêu cá nhân**: ghi chép, phân loại và thống kê thu chi.

Hệ thống sử dụng kết hợp **Java**, **Python** và cơ sở dữ liệu **MySQL**. Java đảm nhiệm phần backend API, Python xử lý Telegram Bot và các tác vụ tự động, còn MySQL lưu trữ dữ liệu học tập của người dùng.

---

## 2. Mục tiêu và kết quả mong muốn

### 2.1. Đối với người dùng

Sau khi hoàn thành, người dùng có thể:

- Quản lý lịch học trực tiếp trên Telegram.
- Thêm, sửa, xóa và xem thời khóa biểu.
- Nhận thông báo lịch học và deadline tự động.
- Theo dõi lịch thi sắp tới.
- Xuất thời khóa biểu và chi tiêu ra Google Sheets.
- Ôn tập từ vựng tiếng Anh bằng chế độ hỏi đáp.
- **Ghi chép thu chi nhanh** ngay trong chat Telegram.
- Xem báo cáo chi tiêu theo ngày, tuần, tháng.
- Đặt ngân sách và nhận cảnh báo khi vượt hạn mức.

### 2.2. Đối với hệ thống

Hệ thống cần đạt các yêu cầu:

- Hoạt động ổn định, có thể chạy liên tục.
- Phản hồi nhanh với các lệnh Telegram.
- Lưu trữ dữ liệu an toàn và có tổ chức.
- Dễ mở rộng thêm tính năng mới.
- Có thể triển khai trên Linux, VPS hoặc cloud server.

---

## 3. Công nghệ sử dụng

### 3.1. Java và Spring Boot

Java được sử dụng để xây dựng backend API, xử lý nghiệp vụ, kết nối database và tích hợp Google Sheets.

**Lý do sử dụng:**

- Hiệu năng ổn định.
- Phù hợp với hệ thống backend có nhiều nghiệp vụ.
- Dễ mở rộng và bảo trì.
- Hệ sinh thái Spring Boot hỗ trợ tốt cho API, bảo mật và database.

### 3.2. Python

Python được sử dụng để xử lý Telegram Bot, scheduler gửi thông báo, hệ thống hỏi đáp từ vựng và các tác vụ automation.

**Thư viện dự kiến:**

- `python-telegram-bot`
- `APScheduler`

**Lý do sử dụng:**

- Phát triển bot nhanh.
- Có nhiều thư viện hỗ trợ Telegram và xử lý lịch.
- Dễ tích hợp thêm AI hoặc NLP trong tương lai.

### 3.3. Telegram Bot API

Telegram Bot API được dùng để:

- Gửi và nhận tin nhắn.
- Tạo các command cho người dùng.
- Gửi thông báo tự động.
- Xử lý callback button và menu tương tác.

### 3.4. MySQL

MySQL được dùng để lưu trữ:

- Thông tin người dùng.
- Thời khóa biểu.
- Deadline bài tập.
- Lịch thi.
- Danh sách từ vựng tiếng Anh.
- Lịch sử học tập và kết quả ôn tập.
- **Giao dịch thu chi** (số tiền, danh mục, ghi chú, ngày giờ).
- **Danh mục chi tiêu** (ăn uống, học phí, giải trí, ...).
- **Ngân sách hàng tháng** theo từng danh mục.

**Lý do sử dụng:**

- Phổ biến và dễ triển khai.
- Hiệu năng tốt với dữ liệu quan hệ.
- Hỗ trợ tốt cho cả Java và Python.
- Phù hợp với bài toán quản lý dữ liệu học tập.

### 3.5. Google Sheets API

Google Sheets API được dùng để:

- Xuất thời khóa biểu ra Google Sheets.
- Xuất danh sách bài tập và lịch thi.
- Xuất báo cáo chi tiêu theo tháng.
- Tự động cập nhật sheet khi có dữ liệu mới.
- Cho phép người dùng xem và chia sẻ dữ liệu dưới dạng bảng tính.

### 3.6. Scheduler

Hệ thống sử dụng scheduler để gửi thông báo đúng thời điểm:

- **Spring Scheduler** cho các tác vụ phía Java.
- **APScheduler** cho các tác vụ phía Python.

**Các tác vụ chính:**

- Nhắc lịch học.
- Nhắc deadline bài tập.
- Nhắc lịch thi.
- Gửi tổng hợp sự kiện học tập trong ngày.

### 3.7. Môi trường triển khai

Hệ thống có thể triển khai trên:

- Ubuntu Server.
- VPS hoặc cloud server.
- AWS, Render, Railway hoặc các nền tảng tương tự.

---

## 4. Tính năng hệ thống

### 4.1. Quản lý thời khóa biểu

Người dùng có thể:

- Thêm môn học.
- Chỉnh sửa lịch học.
- Xóa lịch học.
- Xem lịch học theo ngày hoặc theo tuần.

**Ví dụ command:**

```
/addsubject
/schedule
/timetable
```

### 4.2. Nhắc lịch học và bài tập

Bot tự động gửi thông báo:

- Trước giờ học.
- Trước hạn nộp bài tập.
- Khi deadline sắp đến.

**Ví dụ:**

```
18:30 hôm nay có môn Java Programming.
Deadline báo cáo Linux còn 1 ngày.
```

### 4.3. Thông báo lịch thi sắp đến

Bot hỗ trợ:

- Lưu lịch thi.
- Nhắc trước ngày thi.
- Hiển thị môn thi, phòng thi và thời gian thi.

**Ví dụ:**

```
2 ngày nữa thi môn Cấu trúc dữ liệu.
Phòng thi: A305.
Thời gian: 7:00 sáng.
```

### 4.4. Thông báo sự kiện học tập trong ngày

Mỗi ngày, bot có thể gửi bản tổng hợp gồm:

- Lịch học hôm nay.
- Deadline bài tập.
- Lịch thi gần nhất.
- Nhiệm vụ học tập cần hoàn thành.

**Ví dụ:**

```
Hôm nay:
- Java Programming: 7:00
- Làm bài tập Linux
- Ôn 20 từ vựng TOEIC
```

### 4.5. Xuất dữ liệu ra Google Sheets

Bot có thể tự động xuất dữ liệu ra Google Sheets để người dùng xem và lưu trữ:

- Xuất toàn bộ thời khóa biểu ra sheet **"Lịch học"**.
- Xuất danh sách bài tập & lịch thi ra sheet **"Deadline & Thi"**.
- Xuất báo cáo chi tiêu tháng ra sheet **"Chi tiêu"** kèm bảng tổng hợp.
- Tự động cập nhật khi người dùng thêm/sửa/xóa dữ liệu.

**Ví dụ command:**

```
/export schedule   → Xuất thời khóa biểu ra Sheets
/export expense    → Xuất báo cáo chi tiêu ra Sheets
/export all        → Xuất toàn bộ dữ liệu
```

**Ví dụ phản hồi:**

```
✅ Đã xuất dữ liệu ra Google Sheets!
🔗 https://docs.google.com/spreadsheets/d/...
📊 Sheet "Chi tiêu T6/2025" đã được cập nhật.
```

### 4.6. Chế độ hỏi đáp từ vựng, ngữ pháp

Người dùng có thể thêm từ vựng theo dạng:

```
apple - quả táo
computer - máy tính
```

Bot sẽ:

- Hỏi nghĩa của từ.
- Kiểm tra đáp án.
- Thống kê số câu đúng và sai.

**Ví dụ:**

```
Bot: "computer" nghĩa là gì?
User: máy tính
Bot: Chính xác. ✅
```

Tính năng này có thể mở rộng thành:

- Flashcard.
- Random quiz.
- Spaced repetition.
- Chatbot hỗ trợ học tiếng Anh.

### 4.7. Quản lý chi tiêu cá nhân

Người dùng có thể ghi chép thu chi nhanh chóng ngay trong Telegram.

**Ghi chép giao dịch:**

```
/addexpense 50000 ăn sáng
/addincome 500000 tiền học bổng
```

Hoặc nhập theo hội thoại:

```
Bot: Số tiền?
User: 35000
Bot: Danh mục? (Ăn uống / Di chuyển / Học phí / Giải trí / Khác)
User: Ăn uống
Bot: Ghi chú? (bỏ qua hoặc nhập)
User: cơm trưa
Bot: ✅ Đã ghi: -35,000đ | Ăn uống | cơm trưa
```

**Xem báo cáo:**

```
/report today     → Tổng chi hôm nay
/report week      → Tổng chi 7 ngày qua
/report month     → Báo cáo tháng này theo danh mục
/budget           → Xem ngân sách và mức đã dùng
```

**Ví dụ báo cáo tháng:**

```
📊 Báo cáo tháng 6/2025
─────────────────────────
🍜 Ăn uống:      850,000đ  ████████░░  85%
🚌 Di chuyển:    120,000đ  ████░░░░░░  40%
📚 Học phí:      500,000đ  ██████████ 100%
🎮 Giải trí:       75,000đ  ██░░░░░░░░  25%
─────────────────────────
💸 Tổng chi:   1,545,000đ
💰 Thu nhập:   3,000,000đ
✅ Còn lại:    1,455,000đ
```

**Đặt ngân sách và cảnh báo:**

- Đặt hạn mức chi tiêu theo danh mục mỗi tháng.
- Bot tự động cảnh báo khi đạt 80% và 100% ngân sách.
- Tổng hợp chi tiêu cuối ngày / tuần / tháng.

**Ví dụ cảnh báo:**

```
⚠️ Cảnh báo: Danh mục "Ăn uống" đã dùng 85% ngân sách tháng!
Còn lại: 150,000đ / 1,000,000đ
```

**Danh mục chi tiêu mặc định:**

| Danh mục | Icon | Gợi ý dùng |
|---|---|---|
| Ăn uống | 🍜 | Cơm, cafe, trà sữa |
| Di chuyển | 🚌 | Xe buýt, grab, xăng |
| Học phí & Sách | 📚 | Học phí, giáo trình |
| Giải trí | 🎮 | Game, phim, du lịch |
| Mua sắm | 🛍️ | Quần áo, đồ dùng |
| Y tế | 💊 | Thuốc, khám bệnh |
| Khác | 📦 | Các khoản không phân loại |
---

## 5. Kiến trúc hệ thống

```
Người dùng Telegram
        |
        v
Telegram Bot API
        |
        +---------------------+
        |                     |
        v                     v
Python Bot Service     Java Backend API
        |                     |
        +----------+----------+
                   |
                   v
             MySQL Database
                   |
                   v
          Google Sheets API
```

**Mô tả luồng hoạt động:**

1. Người dùng gửi lệnh hoặc tin nhắn cho bot trên Telegram.
2. **Python Bot Service** tiếp nhận tin nhắn, xử lý các lệnh đơn giản và gọi backend khi cần.
3. **Java Backend API** xử lý nghiệp vụ chính, làm việc với MySQL và Google Sheets.
4. **Scheduler** kiểm tra lịch định kỳ và yêu cầu bot gửi thông báo cho người dùng.

---

## 6. Hướng phát triển tương lai

Các tính năng có thể phát triển thêm:

**Học tập:**
- 🤖 AI hỗ trợ học tập.
- 💬 Chatbot giải bài tập.
- 📅 Gợi ý lịch học tối ưu.
- 🖥️ Dashboard web quản lý học tập.
- 🔗 Đồng bộ Google Classroom.
- 📊 Phân tích tiến độ học tập.
- ✅ Hệ thống điểm danh.
- 🔄 Chế độ ôn tập theo spaced repetition.

**Chi tiêu:**
- 📈 Biểu đồ chi tiêu trực quan (xuất ảnh PNG).
- 🏦 Theo dõi nhiều ví / tài khoản ngân hàng.
- 🔁 Giao dịch định kỳ tự động (học phí, tiền nhà).
- 📤 Xuất báo cáo ra file Excel / CSV.
- 🎯 Mục tiêu tiết kiệm và theo dõi tiến độ.
- 🤝 Chi tiêu nhóm và chia bill.
