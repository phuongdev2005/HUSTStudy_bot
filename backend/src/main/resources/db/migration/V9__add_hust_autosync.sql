-- V9: Thêm cột hỗ trợ auto-sync sự kiện HUST CTSV
-- notify_hust_events: bật/tắt tự động import sự kiện HUST vào deadline mỗi ngày

ALTER TABLE user_settings
    ADD COLUMN notify_hust_events    BOOLEAN     NOT NULL DEFAULT TRUE,
    ADD COLUMN hust_synced_event_ids TEXT        DEFAULT NULL;  -- JSON array: [123, 456, ...]
