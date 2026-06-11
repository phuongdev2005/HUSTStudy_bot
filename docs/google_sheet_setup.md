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

## 2. Format sheet – Dạng lưới ⭐ (Khuyến nghị)

> Bot hỗ trợ **2 format**. Dạng lưới trực quan hơn và dễ nhìn nhất.

### Format lưới (Grid)

**Cột A** = Khung giờ | **Cột B–H** = Từng ngày trong tuần

| **Giờ bắt đầu - Giờ kết thúc** | **Thứ 2** | **Thứ 3** | **Thứ 4** | **Thứ 5** | **Thứ 6** | **Thứ 7** | **Chủ nhật** |
|---|---|---|---|---|---|---|---|
| 00:00 - 06:00 | Ngủ | Ngủ | Ngủ | Ngủ | Ngủ | Ngủ | Ngủ nướng |
| 06:00 - 06:30 | Dậy + Vệ sinh | Dậy + Vệ sinh | Dậy + Vệ sinh | Dậy + Vệ sinh | Dậy + Vệ sinh | Tập thể dục | Ngủ nướng |
| 07:30 - 09:15 | Giải tích 1 (B1-301) | Vật lý ĐC (C9-101) | Giải tích 1 (B1-301) | Vật lý ĐC (C9-201) | CSDL (B1-402) | Ôn bài | |
| 09:30 - 11:00 | Lập trình OOP (B4-Lab1) | Triết học MLN (C7-201) | Tiếng Anh (D3-201) | Lập trình OOP (B4-Lab2) | Tiếng Anh (D3-201) | Học nhóm | Dọn dẹp |
| 11:30 - 12:15 | Ăn trưa (Canteen C1) | Ăn trưa | Ăn trưa | Ăn trưa | Ăn trưa | Ăn trưa | Ăn trưa |
| ... | ... | ... | ... | ... | ... | ... | ... |

**Quy tắc ô:**
- Ô **có nội dung** → tạo 1 hoạt động cho ngày đó
- Ô **để trống** → bỏ qua (không có hoạt động)
- Ghi chú phòng học trong ngoặc đơn: `Giải tích 1 (B1-301)` → bot tự tách ra

---

## 3. Format sheet – Dạng danh sách

Thay thế cho dạng lưới, mỗi dòng = 1 hoạt động:

| A – Thứ | B – Giờ bắt | C – Giờ kết | D – Hoạt động | E – Danh mục | F – Ghi chú |
|---------|------------|------------|--------------|-------------|------------|
| `Tất cả` / `2`–`8` / `CN` | `HH:MM` | `HH:MM` | Tên hoạt động | Tự chọn | Tùy chọn |

**Cột A – Thứ:**

| Giá trị hợp lệ | Ý nghĩa |
|----------------|---------|
| `Tất cả` (hoặc để trống, `*`) | Lặp lại **mọi ngày** (ngủ, ăn, vệ sinh…) |
| `2` hoặc `T2` hoặc `Thứ 2` | Thứ Hai |
| `3` hoặc `T3` | Thứ Ba |
| `4` hoặc `T4` | Thứ Tư |
| `5` hoặc `T5` | Thứ Năm |
| `6` hoặc `T6` | Thứ Sáu |
| `7` hoặc `T7` | Thứ Bảy |
| `8` hoặc `CN` | Chủ Nhật |

**Ví dụ:**
```
Thứ     | Bắt đầu | Kết thúc | Hoạt động         | Danh mục   | Ghi chú
Tất cả  | 00:00   | 06:30    | Ngủ               | Nghỉ ngơi  |
Tất cả  | 06:30   | 07:00    | Vệ sinh cá nhân   | Sinh hoạt  |
Tất cả  | 07:00   | 07:30    | Ăn sáng           | Ăn uống    |
2       | 07:30   | 09:15    | Giải tích 1       | Học tập    | B1-301
2       | 09:30   | 11:00    | Lập trình OOP     | Học tập    | B4-Lab1
```

---

## 4. Danh mục & Emoji tự động

> Bot tự nhận diện danh mục từ tên hoạt động — **không cần nhập tay** (với format lưới)

| Danh mục | Emoji | Từ khóa nhận diện |
|----------|-------|--------------------|
| `Nghỉ ngơi` | 😴 | ngủ, nghỉ, nướng |
| `Sinh hoạt` | 🪥 | vệ sinh, dọn, giặt, dậy, chuẩn bị |
| `Ăn uống` | 🍜 | ăn, canteen, brunch |
| `Học tập` | 📚 | học, thi, ôn, bài, đồ án, thư viện, giải tích, lập trình... |
| `Thể dục` | 🏃 | thể dục, tập, gym, chạy, bóng |
| `Giải trí` | 🎮 | giải trí, youtube, phim, nhạc, chơi, mua sắm |
| `Di chuyển` | 🚌 | di chuyển, xe, đến trường, về nhà |
| `Khác` | 📌 | mọi thứ còn lại |

---

## 5. Import file mẫu có sẵn

File `docs/timetable_template.csv` trong repo là **dạng lưới** đầy đủ 20 khung giờ × 7 ngày:

1. Google Sheets → **File** → **Import**
2. Chọn file `timetable_template.csv`
3. Chọn **Replace spreadsheet**
4. Dấu phân cách: **Comma (,)**
5. Click **Import data**

---

## 6. Cấp quyền cho Bot đọc sheet

> ⚠️ **Bắt buộc** — Bot chỉ đọc được khi bạn cấp quyền!

1. Google Sheet → nút **Share** (góc trên phải)
2. **General access** → chọn `Anyone with the link`
3. Role: `Viewer`
4. Click **Done** ✅

---

## 7. Liên kết và đồng bộ với Bot

```
/setsheet https://docs.google.com/spreadsheets/d/YOUR_SHEET_ID/edit
```

```
/syncsheet
```

> Bot tự nhận dạng format (lưới hay danh sách) — không cần chỉ định.

```
/schedule      ← xem timeline hôm nay
/timetable     ← xem lịch cả tuần
```

---

## 8. Kết quả hiển thị trên Bot

Khi dùng `/schedule` vào **Thứ Hai**:

```
📅 Lịch Thứ Hai, 09/06/2026

`00:00–06:00` 😴 Ngủ
`06:00–06:30` 🪥 Dậy + Vệ sinh
`06:30–07:00` 🍜 Ăn sáng
`07:00–07:30` 🚌 Di chuyển đến trường
`07:30–09:15` 📚 Giải tích 1  _B1-301_
`09:15–09:30` 🪥 Giải lao
`09:30–11:00` 📚 Lập trình OOP  _B4-Lab1_
`11:30–12:15` 🍜 Ăn trưa  _Canteen C1_
`12:15–13:00` 😴 Nghỉ trưa
`13:00–14:30` 📚 Cơ sở dữ liệu  _B1-402_
`14:30–17:30` 📚 Tự học / Làm bài tập
`18:00–18:45` 🍜 Ăn tối
`18:45–20:30` 📚 Ôn bài / Bài tập
`20:30–21:15` 🎮 Giải trí
`22:00–00:00` 😴 Ngủ
```

---

## 9. Lưu ý

- **Sắp xếp** dữ liệu theo giờ tăng dần để hiển thị đúng thứ tự
- **Ô trống** (format lưới) = không có hoạt động ngày đó, bot bỏ qua
- **Ghi chú phòng** ghi trong ngoặc đơn: `Giải tích 1 (B1-301)`
- Sau khi **sửa sheet**, dùng `/syncsheet` để cập nhật bot
- Nếu sheet bị lỗi 403, kiểm tra lại quyền **"Anyone with the link"**
