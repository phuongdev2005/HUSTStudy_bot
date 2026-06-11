-- ============================================================
--  Flyway Migration V3 – Thêm cột google_sheet_url vào user_settings
--  Mỗi user có thể liên kết 1 Google Sheet riêng chứa thời khóa biểu
-- ============================================================

ALTER TABLE user_settings
    ADD COLUMN google_sheet_url VARCHAR(500) NULL
        COMMENT 'Link Google Sheets cá nhân của user (public view)',
    ADD COLUMN sheet_synced_at  DATETIME     NULL
        COMMENT 'Lần cuối sync dữ liệu từ sheet';
