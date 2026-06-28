-- ============================================================
--  Flyway Migration V12 – Thêm trường date cho class_sessions
-- ============================================================

ALTER TABLE class_sessions ADD COLUMN date DATE NULL COMMENT 'Ngày học cụ thể (nếu có)';
