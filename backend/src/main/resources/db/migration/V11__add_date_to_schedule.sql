-- ============================================================
--  Flyway Migration V11 – Thêm trường date cho lịch học & sinh hoạt
-- ============================================================

ALTER TABLE class_schedules ADD COLUMN date DATE NULL COMMENT 'Ngày học cụ thể (nếu có)';
ALTER TABLE daily_activities ADD COLUMN date DATE NULL COMMENT 'Ngày sinh hoạt cụ thể (nếu có)';

-- Cập nhật view v_today_schedule hỗ trợ cả lịch ngày cụ thể và lịch tuần cố định
CREATE OR REPLACE VIEW v_today_schedule AS
SELECT
    cs.id,
    cs.user_id,
    s.name                        AS subject_name,
    s.code                        AS subject_code,
    COALESCE(cs.room, s.room)     AS room,
    cs.start_time,
    cs.end_time,
    cs.remind_before
FROM class_schedules cs
JOIN subjects s ON s.id = cs.subject_id
WHERE cs.is_active = 1
  AND s.is_active  = 1
  AND (
    (cs.date = CURDATE())
    OR (cs.date IS NULL AND cs.day_of_week = WEEKDAY(CURDATE()) + 1)
  );
