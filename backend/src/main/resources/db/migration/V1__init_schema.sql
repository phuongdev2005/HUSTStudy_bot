-- ============================================================
--  Flyway Migration V1 – Tạo toàn bộ bảng
--  File: V1__init_schema.sql
--  Chỉ chứa DDL (CREATE TABLE, INDEX, VIEW)
--  Không có INSERT data – seed riêng ở V2
-- ============================================================

-- ============================================================
-- 1. USERS
-- ============================================================
CREATE TABLE IF NOT EXISTS users (
    id              BIGINT          NOT NULL AUTO_INCREMENT,
    telegram_id     BIGINT          NOT NULL UNIQUE COMMENT 'Telegram chat_id',
    username        VARCHAR(100)    COMMENT 'Telegram @username (có thể null)',
    full_name       VARCHAR(255)    NOT NULL COMMENT 'Tên hiển thị trên Telegram',
    language_code   VARCHAR(10)     DEFAULT 'vi',
    timezone        VARCHAR(50)     DEFAULT 'Asia/Ho_Chi_Minh',
    is_active       TINYINT(1)      NOT NULL DEFAULT 1,
    created_at      DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at      DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

    PRIMARY KEY (id),
    INDEX idx_telegram_id (telegram_id)
) COMMENT 'Người dùng đăng ký bot';

-- ============================================================
-- 2. SUBJECTS
-- ============================================================
CREATE TABLE IF NOT EXISTS subjects (
    id              BIGINT          NOT NULL AUTO_INCREMENT,
    user_id         BIGINT          NOT NULL,
    name            VARCHAR(255)    NOT NULL,
    code            VARCHAR(50),
    teacher         VARCHAR(255),
    room            VARCHAR(50),
    credits         TINYINT         DEFAULT 3,
    semester        VARCHAR(20),
    color           VARCHAR(7)      DEFAULT '#4A90D9',
    is_active       TINYINT(1)      NOT NULL DEFAULT 1,
    created_at      DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at      DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

    PRIMARY KEY (id),
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_subject_user (user_id)
) COMMENT 'Danh sách môn học';

-- ============================================================
-- 3. CLASS_SCHEDULES
-- ============================================================
CREATE TABLE IF NOT EXISTS class_schedules (
    id              BIGINT          NOT NULL AUTO_INCREMENT,
    subject_id      BIGINT          NOT NULL,
    user_id         BIGINT          NOT NULL,
    day_of_week     TINYINT         NOT NULL COMMENT '1=T2 2=T3 3=T4 4=T5 5=T6 6=T7 7=CN',
    start_time      TIME            NOT NULL,
    end_time        TIME            NOT NULL,
    room            VARCHAR(50),
    remind_before   SMALLINT        DEFAULT 30 COMMENT 'Nhắc trước X phút',
    is_active       TINYINT(1)      NOT NULL DEFAULT 1,
    created_at      DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at      DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

    PRIMARY KEY (id),
    FOREIGN KEY (subject_id) REFERENCES subjects(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id)    REFERENCES users(id)    ON DELETE CASCADE,
    INDEX idx_schedule_user_day (user_id, day_of_week)
) COMMENT 'Thời khóa biểu hàng tuần';

-- ============================================================
-- 4. DEADLINES
-- ============================================================
CREATE TABLE IF NOT EXISTS deadlines (
    id              BIGINT          NOT NULL AUTO_INCREMENT,
    user_id         BIGINT          NOT NULL,
    subject_id      BIGINT          COMMENT 'Nullable – không bắt buộc liên kết môn',
    title           VARCHAR(255)    NOT NULL,
    description     TEXT,
    due_date        DATETIME        NOT NULL,
    priority        ENUM('LOW','MEDIUM','HIGH') DEFAULT 'MEDIUM',
    status          ENUM('PENDING','DONE','OVERDUE') DEFAULT 'PENDING',
    remind_before   SMALLINT        DEFAULT 1440 COMMENT 'Nhắc trước X phút (mặc định 1 ngày)',
    is_notified     TINYINT(1)      DEFAULT 0,
    created_at      DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at      DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

    PRIMARY KEY (id),
    FOREIGN KEY (user_id)    REFERENCES users(id)    ON DELETE CASCADE,
    FOREIGN KEY (subject_id) REFERENCES subjects(id) ON DELETE SET NULL,
    INDEX idx_deadline_user_due (user_id, due_date),
    INDEX idx_deadline_status (status)
) COMMENT 'Deadline bài tập';

-- ============================================================
-- 5. EXAMS
-- ============================================================
CREATE TABLE IF NOT EXISTS exams (
    id              BIGINT          NOT NULL AUTO_INCREMENT,
    user_id         BIGINT          NOT NULL,
    subject_id      BIGINT          COMMENT 'Nullable',
    subject_name    VARCHAR(255)    NOT NULL COMMENT 'Lưu riêng phòng khi xóa môn',
    exam_date       DATETIME        NOT NULL,
    duration_min    SMALLINT        DEFAULT 90,
    room            VARCHAR(50),
    exam_type       ENUM('MIDTERM','FINAL','MAKEUP','OTHER') DEFAULT 'FINAL',
    note            TEXT,
    remind_days     TINYINT         DEFAULT 2,
    is_notified     TINYINT(1)      DEFAULT 0,
    created_at      DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at      DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

    PRIMARY KEY (id),
    FOREIGN KEY (user_id)    REFERENCES users(id)    ON DELETE CASCADE,
    FOREIGN KEY (subject_id) REFERENCES subjects(id) ON DELETE SET NULL,
    INDEX idx_exam_user_date (user_id, exam_date)
) COMMENT 'Lịch thi';

-- ============================================================
-- 6. VOCABULARIES
-- ============================================================
CREATE TABLE IF NOT EXISTS vocabularies (
    id              BIGINT          NOT NULL AUTO_INCREMENT,
    user_id         BIGINT          NOT NULL,
    word            VARCHAR(255)    NOT NULL,
    meaning         TEXT            NOT NULL,
    pronunciation   VARCHAR(255),
    example         TEXT,
    category        VARCHAR(100),
    next_review_at  DATETIME        COMMENT 'Spaced Repetition – lần ôn tiếp theo',
    review_interval SMALLINT        DEFAULT 1 COMMENT 'Chu kỳ ôn (ngày)',
    ease_factor     DECIMAL(4,2)    DEFAULT 2.50 COMMENT 'Hệ số SM-2',
    times_seen      INT             DEFAULT 0,
    times_correct   INT             DEFAULT 0,
    created_at      DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at      DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

    PRIMARY KEY (id),
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_vocab_user (user_id, word),
    INDEX idx_vocab_review (user_id, next_review_at)
) COMMENT 'Từ vựng tiếng Anh';

-- ============================================================
-- 7. VOCAB_SESSIONS
-- ============================================================
CREATE TABLE IF NOT EXISTS vocab_sessions (
    id              BIGINT          NOT NULL AUTO_INCREMENT,
    user_id         BIGINT          NOT NULL,
    started_at      DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP,
    ended_at        DATETIME,
    total_questions INT             DEFAULT 0,
    correct_count   INT             DEFAULT 0,
    wrong_count     INT             DEFAULT 0,
    status          ENUM('IN_PROGRESS','DONE','ABANDONED') DEFAULT 'IN_PROGRESS',

    PRIMARY KEY (id),
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_vocab_session_user (user_id, started_at)
) COMMENT 'Phiên quiz từ vựng';

-- ============================================================
-- 8. VOCAB_ANSWERS
-- ============================================================
CREATE TABLE IF NOT EXISTS vocab_answers (
    id              BIGINT          NOT NULL AUTO_INCREMENT,
    session_id      BIGINT          NOT NULL,
    vocab_id        BIGINT          NOT NULL,
    user_answer     TEXT,
    is_correct      TINYINT(1)      NOT NULL DEFAULT 0,
    response_time   SMALLINT        COMMENT 'Thời gian trả lời (giây)',
    answered_at     DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP,

    PRIMARY KEY (id),
    FOREIGN KEY (session_id) REFERENCES vocab_sessions(id) ON DELETE CASCADE,
    FOREIGN KEY (vocab_id)   REFERENCES vocabularies(id)   ON DELETE CASCADE
) COMMENT 'Kết quả từng câu quiz';

-- ============================================================
-- 9. EXPENSE_CATEGORIES
-- ============================================================
CREATE TABLE IF NOT EXISTS expense_categories (
    id              INT             NOT NULL AUTO_INCREMENT,
    user_id         BIGINT          COMMENT 'NULL = danh mục hệ thống mặc định',
    name            VARCHAR(100)    NOT NULL,
    icon            VARCHAR(10),
    type            ENUM('EXPENSE','INCOME','BOTH') DEFAULT 'EXPENSE',
    is_default      TINYINT(1)      DEFAULT 0,
    is_active       TINYINT(1)      DEFAULT 1,
    sort_order      TINYINT         DEFAULT 0,

    PRIMARY KEY (id),
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_category_user (user_id)
) COMMENT 'Danh mục thu chi';

-- ============================================================
-- 10. EXPENSES
-- ============================================================
CREATE TABLE IF NOT EXISTS expenses (
    id              BIGINT          NOT NULL AUTO_INCREMENT,
    user_id         BIGINT          NOT NULL,
    category_id     INT             NOT NULL,
    type            ENUM('EXPENSE','INCOME') NOT NULL DEFAULT 'EXPENSE',
    amount          DECIMAL(15,2)   NOT NULL,
    note            VARCHAR(500),
    transaction_at  DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP,
    created_at      DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at      DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

    PRIMARY KEY (id),
    FOREIGN KEY (user_id)     REFERENCES users(id)              ON DELETE CASCADE,
    FOREIGN KEY (category_id) REFERENCES expense_categories(id) ON DELETE RESTRICT,
    INDEX idx_expense_user_month (user_id, transaction_at),
    INDEX idx_expense_user_type  (user_id, type)
) COMMENT 'Giao dịch thu chi';

-- ============================================================
-- 11. BUDGETS
-- ============================================================
CREATE TABLE IF NOT EXISTS budgets (
    id              BIGINT          NOT NULL AUTO_INCREMENT,
    user_id         BIGINT          NOT NULL,
    category_id     INT             NOT NULL,
    month           TINYINT         NOT NULL,
    year            SMALLINT        NOT NULL,
    amount          DECIMAL(15,2)   NOT NULL,
    warn_threshold  DECIMAL(4,2)    DEFAULT 0.80,
    is_notified_80  TINYINT(1)      DEFAULT 0,
    is_notified_100 TINYINT(1)      DEFAULT 0,
    created_at      DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at      DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

    PRIMARY KEY (id),
    UNIQUE KEY uq_budget (user_id, category_id, month, year),
    FOREIGN KEY (user_id)     REFERENCES users(id)              ON DELETE CASCADE,
    FOREIGN KEY (category_id) REFERENCES expense_categories(id) ON DELETE CASCADE,
    INDEX idx_budget_user_period (user_id, year, month)
) COMMENT 'Ngân sách hàng tháng';

-- ============================================================
-- 12. NOTIFICATION_LOGS
-- ============================================================
CREATE TABLE IF NOT EXISTS notification_logs (
    id              BIGINT          NOT NULL AUTO_INCREMENT,
    user_id         BIGINT          NOT NULL,
    type            ENUM('CLASS_REMIND','DEADLINE_REMIND','EXAM_REMIND','BUDGET_WARN','DAILY_SUMMARY') NOT NULL,
    ref_id          BIGINT          COMMENT 'ID record liên quan',
    message         TEXT,
    sent_at         DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP,
    status          ENUM('SENT','FAILED') DEFAULT 'SENT',

    PRIMARY KEY (id),
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_notif_user_type (user_id, type, sent_at)
) COMMENT 'Lịch sử thông báo';

-- ============================================================
-- 13. USER_SETTINGS
-- ============================================================
CREATE TABLE IF NOT EXISTS user_settings (
    id                      BIGINT      NOT NULL AUTO_INCREMENT,
    user_id                 BIGINT      NOT NULL UNIQUE,
    notify_class_remind     TINYINT(1)  DEFAULT 1,
    notify_deadline         TINYINT(1)  DEFAULT 1,
    notify_exam             TINYINT(1)  DEFAULT 1,
    notify_budget_warn      TINYINT(1)  DEFAULT 1,
    notify_daily_summary    TINYINT(1)  DEFAULT 1,
    daily_summary_time      TIME        DEFAULT '07:00:00',
    class_remind_before     SMALLINT    DEFAULT 30,
    deadline_remind_before  SMALLINT    DEFAULT 1440,
    exam_remind_before_days TINYINT     DEFAULT 2,
    updated_at              DATETIME    NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

    PRIMARY KEY (id),
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
) COMMENT 'Cài đặt thông báo người dùng';

-- ============================================================
-- VIEWS
-- ============================================================

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
  AND cs.day_of_week = DAYOFWEEK(CURDATE()) - 1;

CREATE OR REPLACE VIEW v_upcoming_deadlines AS
SELECT
    d.id,
    d.user_id,
    d.title,
    d.due_date,
    d.priority,
    d.status,
    s.name AS subject_name,
    TIMESTAMPDIFF(HOUR, NOW(), d.due_date) AS hours_left
FROM deadlines d
LEFT JOIN subjects s ON s.id = d.subject_id
WHERE d.status = 'PENDING'
  AND d.due_date BETWEEN NOW() AND DATE_ADD(NOW(), INTERVAL 7 DAY);

CREATE OR REPLACE VIEW v_upcoming_exams AS
SELECT
    e.id,
    e.user_id,
    e.subject_name,
    e.exam_date,
    e.room,
    e.exam_type,
    e.duration_min,
    DATEDIFF(e.exam_date, CURDATE()) AS days_left
FROM exams e
WHERE e.exam_date > NOW()
  AND e.exam_date <= DATE_ADD(NOW(), INTERVAL 30 DAY);

CREATE OR REPLACE VIEW v_monthly_expense_summary AS
SELECT
    ex.user_id,
    ec.id                           AS category_id,
    ec.name                         AS category_name,
    ec.icon,
    ex.type,
    SUM(ex.amount)                  AS total_amount,
    COUNT(*)                        AS transaction_count,
    MONTH(ex.transaction_at)        AS month,
    YEAR(ex.transaction_at)         AS year
FROM expenses ex
JOIN expense_categories ec ON ec.id = ex.category_id
GROUP BY ex.user_id, ec.id, ec.name, ec.icon, ex.type,
         MONTH(ex.transaction_at), YEAR(ex.transaction_at);

CREATE OR REPLACE VIEW v_budget_status AS
SELECT
    b.user_id,
    b.category_id,
    ec.name                                                         AS category_name,
    ec.icon,
    b.month,
    b.year,
    b.amount                                                        AS budget_amount,
    COALESCE(SUM(ex.amount), 0)                                     AS spent_amount,
    ROUND(COALESCE(SUM(ex.amount), 0) / b.amount * 100, 1)         AS spent_pct,
    b.warn_threshold,
    b.is_notified_80,
    b.is_notified_100
FROM budgets b
JOIN expense_categories ec ON ec.id = b.category_id
LEFT JOIN expenses ex
       ON ex.user_id      = b.user_id
      AND ex.category_id  = b.category_id
      AND ex.type         = 'EXPENSE'
      AND MONTH(ex.transaction_at) = b.month
      AND YEAR(ex.transaction_at)  = b.year
GROUP BY b.id, b.user_id, b.category_id, ec.name, ec.icon,
         b.month, b.year, b.amount, b.warn_threshold,
         b.is_notified_80, b.is_notified_100;
