-- ============================================================
--  Flyway Migration V4 – Bảng lịch sinh hoạt hằng ngày
--  Thay thế subjects + class_schedules cho tính năng /schedule
--  Mỗi dòng = 1 khung giờ hoạt động (ngủ, học, ăn, vệ sinh...)
-- ============================================================

CREATE TABLE IF NOT EXISTS daily_activities (
    id          BIGINT       NOT NULL AUTO_INCREMENT,
    user_id     BIGINT       NOT NULL,

    -- NULL = lặp lại mọi ngày; 1=T2 2=T3 3=T4 4=T5 5=T6 6=T7 7=CN
    day_of_week TINYINT      NULL         COMMENT 'NULL=mọi ngày, 1=T2..7=CN',

    start_time  TIME         NOT NULL     COMMENT 'HH:MM',
    end_time    TIME         NOT NULL     COMMENT 'HH:MM',
    activity    VARCHAR(255) NOT NULL     COMMENT 'Tên hoạt động',
    category    VARCHAR(50)  NOT NULL DEFAULT 'Khác'
                             COMMENT 'Nghỉ ngơi|Sinh hoạt|Ăn uống|Học tập|Thể dục|Giải trí|Di chuyển|Khác',
    note        VARCHAR(500) NULL         COMMENT 'Ghi chú (phòng học, địa điểm...)',
    sort_order  SMALLINT     NOT NULL DEFAULT 0,

    created_at  DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at  DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

    PRIMARY KEY (id),
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_activity_user_day (user_id, day_of_week),
    INDEX idx_activity_user_time (user_id, start_time)
) COMMENT 'Lịch sinh hoạt hằng ngày của user (toàn bộ timeline)';
