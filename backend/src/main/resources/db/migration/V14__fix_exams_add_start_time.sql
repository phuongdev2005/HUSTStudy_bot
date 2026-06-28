-- ============================================================
--  V14: Thêm cột start_time vào bảng exams
--  Dùng IF NOT EXISTS để migration an toàn khi đã apply dở trước đó.
-- ============================================================

ALTER TABLE exams
    ADD COLUMN IF NOT EXISTS start_time TIME NULL COMMENT 'Giờ bắt đầu thi (HH:MM:SS)' AFTER exam_date;
