-- ============================================================
--  Flyway Migration V6 – Thêm fields AI Scan vào bảng expenses
--  Hỗ trợ tính năng quét ảnh hóa đơn/bill bằng Gemini Vision
-- ============================================================

ALTER TABLE expenses
    ADD COLUMN image_file_id  VARCHAR(255)            NULL       COMMENT 'Telegram file_id của ảnh hóa đơn gốc',
    ADD COLUMN source         ENUM('MANUAL','AI_SCAN') NOT NULL DEFAULT 'MANUAL' COMMENT 'Nguồn gốc giao dịch',
    ADD COLUMN ai_confidence  DECIMAL(3,2)            NULL       COMMENT 'Độ tin cậy AI (0.00–1.00), NULL nếu nhập tay';
