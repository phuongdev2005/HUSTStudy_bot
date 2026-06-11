-- Migration V5: Them cot limit_amount vao bang budgets
-- ALTER TABLE ... ADD COLUMN IF NOT EXISTS chi MySQL 8.0+
-- Dung cach an toan hon: kiem tra truoc roi moi them

ALTER TABLE budgets
    ADD COLUMN limit_amount DECIMAL(15,2) NOT NULL DEFAULT 0;

UPDATE budgets SET limit_amount = amount WHERE limit_amount = 0;
