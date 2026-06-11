-- ============================================================
--  Flyway Migration V2 – Seed dữ liệu hệ thống mặc định
--  File: V2__seed_default_categories.sql
--
--  Chỉ INSERT dữ liệu tĩnh do hệ thống quản lý (user_id = NULL).
--  Dữ liệu người dùng KHÔNG seed ở đây – được tạo qua API.
-- ============================================================

INSERT INTO expense_categories (user_id, name, icon, type, is_default, sort_order) VALUES
(NULL, 'Ăn uống',        '🍜', 'EXPENSE', 1,  1),
(NULL, 'Di chuyển',      '🚌', 'EXPENSE', 1,  2),
(NULL, 'Học phí & Sách', '📚', 'EXPENSE', 1,  3),
(NULL, 'Giải trí',       '🎮', 'EXPENSE', 1,  4),
(NULL, 'Mua sắm',        '🛍️', 'EXPENSE', 1,  5),
(NULL, 'Y tế',           '💊', 'EXPENSE', 1,  6),
(NULL, 'Khác',           '📦', 'EXPENSE', 1,  7),
(NULL, 'Học bổng',       '🎓', 'INCOME',  1,  8),
(NULL, 'Lương / Trợ cấp','💵', 'INCOME',  1,  9),
(NULL, 'Thu nhập khác',  '💰', 'INCOME',  1, 10);
