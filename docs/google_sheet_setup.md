# 📋 Hướng Dẫn Tạo Google Sheet Thời Khóa Biểu

## 1. Tạo Google Sheet mới

1. Vào [Google Sheets](https://sheets.google.com) → **Tạo bảng tính mới**
2. Đặt tên: `TKB - [Tên bạn] - HK2024.2`

---

## 2. Format bắt buộc

> **Hàng 1 = Header** (giữ nguyên tiêu đề), **Từ hàng 2 = Dữ liệu**

| Cột A | Cột B | Cột C | Cột D | Cột E | Cột F | Cột G |
|-------|-------|-------|-------|-------|-------|-------|
| Tên môn | Mã môn | Thứ | Giờ bắt đầu | Giờ kết thúc | Phòng | Giảng viên |

### Quy tắc cột **Thứ** (Cột C):
| Giá trị hợp lệ | Ý nghĩa |
|----------------|---------|
| `2` hoặc `T2` | Thứ Hai |
| `3` hoặc `T3` | Thứ Ba |
| `4` hoặc `T4` | Thứ Tư |
| `5` hoặc `T5` | Thứ Năm |
| `6` hoặc `T6` | Thứ Sáu |
| `7` hoặc `T7` | Thứ Bảy |
| `8` hoặc `CN` | Chủ Nhật |

### Quy tắc cột **Giờ** (Cột D & E):
- Format: `HH:MM` (24h)
- Ví dụ: `07:00`, `09:30`, `13:00`

---

## 3. Dữ liệu mẫu

Sao chép dữ liệu dưới đây vào sheet của bạn (bỏ qua dòng header nếu đã có):

```
Tên môn         | Mã môn  | Thứ | Giờ bắt | Giờ kết | Phòng    | Giảng viên
Giải tích 1     | MA1010  |  2  | 07:00   | 09:30   | B1-301   | Nguyễn Văn An
Vật lý ĐC 1    | PH1010  |  2  | 13:00   | 15:30   | C9-101   | Trần Thị Bình
Lập trình OOP   | IT3080  |  3  | 07:00   | 09:30   | B1-401   | Lê Văn Chính
Triết học MLN   | SSH1110 |  3  | 13:00   | 15:30   | C7-201   | Phạm Thị Dung
Giải tích 1     | MA1010  |  4  | 09:45   | 12:15   | B1-301   | Nguyễn Văn An
Cơ sở dữ liệu   | IT3090  |  4  | 13:00   | 15:30   | B4-Lab1  | Hoàng Văn Em
Lập trình OOP   | IT3080  |  5  | 07:00   | 09:30   | B4-Lab2  | Lê Văn Chính
Vật lý ĐC 1    | PH1010  |  5  | 13:00   | 14:30   | C9-201   | Trần Thị Bình
Cơ sở dữ liệu   | IT3090  |  6  | 07:00   | 09:30   | B1-402   | Hoàng Văn Em
Tiếng Anh B1    | FL1101  |  6  | 09:45   | 11:15   | D3-201   | Smith John
```

---

## 4. Import file CSV có sẵn

Thay vì nhập tay, bạn có thể import file `timetable_template.csv` trong repo:

1. Google Sheets → **File** → **Import**
2. Chọn file `docs/timetable_template.csv`
3. Chọn **Replace spreadsheet** hoặc **Insert new sheet**
4. Dấu phân cách: **Comma (,)**

---

## 5. Cấp quyền truy cập cho Bot

> ⚠️ **QUAN TRỌNG**: Bot chỉ đọc được sheet khi bạn cấp quyền!

1. Mở Google Sheet → **Share** (nút xanh góc trên phải)
2. Trong phần **General access**, chọn **"Anyone with the link"**
3. Chọn role: **Viewer**
4. Click **Done**

---

## 6. Liên kết với Bot

Copy link sheet (dạng `https://docs.google.com/spreadsheets/d/...`) rồi gửi cho bot:

```
/setsheet https://docs.google.com/spreadsheets/d/YOUR_SHEET_ID/edit
```

Sau đó đồng bộ dữ liệu:
```
/syncsheet
```

Xem lịch hôm nay:
```
/schedule
```

---

## 7. Lưu ý

- 1 dòng = 1 **buổi học** (cùng môn học 2 buổi/tuần → 2 dòng)
- Cột **Mã môn** và **Giảng viên** có thể để trống
- Phòng học có thể để trống
- Không để trống **Tên môn**, **Thứ**, **Giờ bắt**, **Giờ kết**
- Sau khi sửa sheet, dùng `/syncsheet` để cập nhật bot

