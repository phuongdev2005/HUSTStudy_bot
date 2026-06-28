-- ============================================================
--  Flyway Migration V10 - Create missing tables for Java entities
--  Note: Uses standard SQL only (no DELIMITER, no stored procedures)
-- ============================================================

-- ── class_sessions (Java entity ClassSession uses this table) ─
CREATE TABLE IF NOT EXISTS class_sessions (
    id          BIGINT      NOT NULL AUTO_INCREMENT,
    subject_id  BIGINT      NOT NULL,
    day_of_week INT         NOT NULL COMMENT '1=Mon ... 7=Sun',
    start_time  VARCHAR(5)  NOT NULL COMMENT 'HH:mm',
    end_time    VARCHAR(5)  NOT NULL COMMENT 'HH:mm',
    room        VARCHAR(100),
    week_type   VARCHAR(20) DEFAULT 'ALL',
    created_at  DATETIME    NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at  DATETIME    NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (id),
    FOREIGN KEY (subject_id) REFERENCES subjects(id) ON DELETE CASCADE,
    INDEX idx_session_day (day_of_week)
);

-- ── words (Java entity Word - spaced repetition) ─────────────
CREATE TABLE IF NOT EXISTS words (
    id              BIGINT       NOT NULL AUTO_INCREMENT,
    user_id         BIGINT       NOT NULL,
    word            VARCHAR(200) NOT NULL,
    meaning         VARCHAR(500) NOT NULL,
    example         TEXT,
    pronunciation   VARCHAR(200),
    level           INT          NOT NULL DEFAULT 0,
    next_review_at  DATETIME,
    created_at      DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (id),
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_word_user_review (user_id, next_review_at)
);

-- ── deadlines: add missing columns (no-op if column exists) ──
-- subject column
ALTER TABLE deadlines ADD subject VARCHAR(200);

-- is_done column
ALTER TABLE deadlines ADD is_done TINYINT(1) NOT NULL DEFAULT 0;

-- ── exams: add missing columns ────────────────────────────────
ALTER TABLE exams ADD subject          VARCHAR(200);
ALTER TABLE exams ADD start_time       TIME;
ALTER TABLE exams ADD duration_minutes INT;
ALTER TABLE exams ADD exam_type_text   VARCHAR(50);
