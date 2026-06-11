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

### 4.1. Quản lý thời khóa biểu hoạt động hằng ngày.

+ thêm lịch học trên trường. thêm lịch làm việc cá nhân + từ google sheet.

- Chỉnh sửa lịch học.
- Xem lịch học theo ngày hoặc theo tuần.

**các command:**

```
/connectsheet
/sync

/schedule
/timetable

/addsubject
/editsubject
/deletesubject

/adddeadline
/deadlines
/deletedeadline

/notification
/remind

/stats
/help
```

4.2 Quản lý lịch thi và deadline

- Import lịch thi từ file sheet của trường -> so khớp với thời khóa biểu -> tìm đúng lịch thi.
- Thêm lịch thi thủ công
- Đếm ngược đến ngày thi
- Lịch thi tuần này
- Quản lý deadline bài tập
- Đánh dấu đã hoàn thành
- Mức độ ưu tiên

### 4.3. Thông báo hằng ngày( sự kiện ĐRL, sự kiện sắp đến, quiz từ vựng ngẫu nhiên)

Mỗi ngày, bot có thể gửi bản tổng hợp gồm:

- Đang giờ này đang là giờ gì
- Deadline bài tập.
- Lịch thi gần nhất.
- Nhiệm vụ học tập cần hoàn thành.

### 4.4. Chế độ hỏi đáp từ vựng , ngữ pháp

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

### 4.5. Quản lý chi tiêu cá nhân

- đưa vào ảnh  lấy note chji tiêu


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
