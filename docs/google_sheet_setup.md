# 📋 Hướng Dẫn Tạo Google Sheet Lịch Sinh Hoạt Hằng Ngày

## Ý tưởng

Mỗi user có **1 Google Sheet riêng** chứa toàn bộ lịch sinh hoạt trong ngày:
ngủ, vệ sinh, ăn uống, đi học, tập thể dục, giải trí...

Bot sẽ đọc sheet này và hiển thị **timeline đẹp** khi bạn dùng `/schedule`.

---

## 1. Tạo Google Sheet mới

1. Vào [sheets.google.com](https://sheets.google.com) → **Tạo bảng tính mới (+)**
2. Đặt tên: `Lịch sinh hoạt – [Tên bạn] – HK2024.2`

---

## 2. Format bắt buộc (6 cột)

> **Hàng 1 = Header** (giữ nguyên), **Từ hàng 2 = Dữ liệu**

| A – Thứ | B – Giờ bắt | C – Giờ kết | D – Hoạt động | E – Danh mục | F – Ghi chú |
|---------|------------|------------|--------------|-------------|------------|
| `Tất cả` / `2`–`8` | `HH:MM` | `HH:MM` | Tên hoạt động | Danh mục | Tùy chọn |

### Cột A – Thứ:
| Giá trị | Ý nghĩa |
|---------|---------|
| `Tất cả` (hoặc `*`, để trống) | Lặp lại **mọi ngày** (ngủ, ăn, vệ sinh…) |
| `2` hoặc `T2` | Thứ Hai |
| `3` hoặc `T3` | Thứ Ba |
| `4` hoặc `T4` | Thứ Tư |
| `5` hoặc `T5` | Thứ Năm |
| `6` hoặc `T6` | Thứ Sáu |
| `7` hoặc `T7` | Thứ Bảy |
| `8` hoặc `CN` | Chủ Nhật |

### Cột E – Danh mục (có emoji tự động):
| Danh mục | Emoji | Ví dụ |
|----------|-------|-------|
| `Nghỉ ngơi` | 😴 | Ngủ, nghỉ trưa |
| `Sinh hoạt` | 🪥 | Vệ sinh, chuẩn bị ngủ |
| `Ăn uống` | 🍜 | Ăn sáng, ăn trưa, ăn tối |
| `Học tập` | 📚 | Lịch học, ôn bài |
| `Thể dục` | 🏃 | Tập gym, chạy bộ |
| `Giải trí` | 🎮 | Xem phim, đọc sách |
| `Di chuyển` | 🚌 | Đi học, đi về |
| `Khác` | 📌 | Mọi thứ còn lại |

---

## 3. Ví dụ lịch mẫu

```
Thứ     | Bắt đầu | Kết thúc | Hoạt động         | Danh mục   | Ghi chú
Tất cả  | 00:00   | 06:30    | Ngủ               | Nghỉ ngơi  |
Tất cả  | 06:30   | 06:50    | Vệ sinh cá nhân   | Sinh hoạt  |
Tất cả  | 06:50   | 07:20    | Ăn sáng           | Ăn uống    |
Tất cả  | 07:20   | 07:40    | Di chuyển đi học  | Di chuyển  | Xe buýt 32
2       | 07:30   | 09:30    | Giải tích 1       | Học tập    | B1-301
2       | 09:30   | 11:30    | Lập trình OOP     | Học tập    | B4-Lab1
2       | 11:30   | 12:30    | Ăn trưa           | Ăn uống    | Canteen C1
Tất cả  | 18:00   | 18:30    | Ăn tối            | Ăn uống    |
Tất cả  | 18:30   | 20:00    | Ôn bài            | Học tập    |
Tất cả  | 22:00   | 00:00    | Ngủ               | Nghỉ ngơi  |
```

---

## 4. Import file mẫu có sẵn

File `docs/timetable_template.csv` trong repo đã có sẵn 28 dòng mẫu:

1. Google Sheets → **File** → **Import**
2. Chọn file `timetable_template.csv`
3. **Replace spreadsheet** / **Insert new sheet**
4. Dấu phân cách: **Comma (,)**

---

## 5. Cấp quyền cho Bot đọc sheet

> ⚠️ **Bắt buộc** — Bot chỉ đọc được khi bạn cấp quyền!

1. Google Sheet → **Share** (nút xanh góc phải)
2. **General access** → chọn `Anyone with the link`
3. Role: `Viewer`
4. Click **Done**

---

## 6. Liên kết và đồng bộ với Bot

```
/setsheet https://docs.google.com/spreadsheets/d/YOUR_ID/edit
```
```
/syncsheet
```
```
/schedule      ← xem lịch hôm nay
/timetable     ← xem lịch cả tuần
```

---

## 7. Kết quả hiển thị trên Bot

Khi dùng `/schedule`, bot sẽ hiện timeline như sau:

```
📅 Lịch Thứ Hai, 09/06/2026

00:00–06:30 😴 Ngủ
06:30–06:50 🪥 Vệ sinh cá nhân
06:50–07:20 🍜 Ăn sáng
07:20–07:40 🚌 Di chuyển đến trường  xe buýt 32
────────────────────
07:30–09:30 📚 Giải tích 1  B1-301
09:30–11:30 📚 Lập trình OOP  B4-Lab1
11:30–12:30 🍜 Ăn trưa  Canteen C1
12:30–13:00 😴 Nghỉ trưa
13:00–15:30 📚 Cơ sở dữ liệu  B1-402
────────────────────
18:00–18:30 🍜 Ăn tối
18:30–20:00 📚 Ôn bài
20:00–21:00 🎮 Giải trí  YouTube / đọc sách
22:00–00:00 😴 Ngủ
```

---

## 8. Lưu ý

- Sắp xếp dữ liệu theo **giờ tăng dần** để hiển thị đúng thứ tự
- Hàng `Tất cả` sẽ hiện **mọi ngày** → dùng cho routine cố định
- Có thể để trống cột **Ghi chú** và **Danh mục**
- Sau khi sửa sheet, dùng `/syncsheet` để cập nhật bot
