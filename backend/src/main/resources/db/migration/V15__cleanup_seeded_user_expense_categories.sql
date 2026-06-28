-- Keep one safe fallback category per user and remove old seeded samples.
-- Categories referenced by historical rows are reassigned to the user's "Khác"
-- before deletion to avoid foreign-key failures.

INSERT INTO expense_categories (user_id, name, icon, type, is_default, is_active, sort_order)
SELECT u.id, 'Khác', '📦', 'EXPENSE', 1, 1, 0
FROM users u
WHERE NOT EXISTS (
    SELECT 1
    FROM expense_categories c
    WHERE c.user_id = u.id
      AND LOWER(c.name) = LOWER('Khác')
);

UPDATE expense_categories c
SET c.is_active = 1,
    c.is_default = 1,
    c.icon = COALESCE(NULLIF(c.icon, ''), '📦'),
    c.type = 'EXPENSE',
    c.sort_order = 0
WHERE c.user_id IS NOT NULL
  AND LOWER(c.name) = LOWER('Khác');

UPDATE expenses e
JOIN expense_categories old_cat ON old_cat.id = e.category_id
JOIN expense_categories other_cat
  ON other_cat.user_id = e.user_id
 AND LOWER(other_cat.name) = LOWER('Khác')
SET e.category_id = other_cat.id
WHERE old_cat.name IN (
    'Ăn uống',
    'Di chuyển',
    'Học phí & Sách',
    'Giải trí',
    'Mua sắm',
    'Y tế',
    'Học bổng',
    'Lương / Trợ cấp',
    'Thu nhập khác'
);

DELETE c
FROM expense_categories c
LEFT JOIN expenses e ON e.category_id = c.id
LEFT JOIN budgets b ON b.category_id = c.id
WHERE c.name IN (
    'Ăn uống',
    'Di chuyển',
    'Học phí & Sách',
    'Giải trí',
    'Mua sắm',
    'Y tế',
    'Học bổng',
    'Lương / Trợ cấp',
    'Thu nhập khác'
)
AND e.id IS NULL
AND b.id IS NULL;

UPDATE expense_categories c
SET c.is_active = 0
WHERE c.name IN (
    'Ăn uống',
    'Di chuyển',
    'Học phí & Sách',
    'Giải trí',
    'Mua sắm',
    'Y tế',
    'Học bổng',
    'Lương / Trợ cấp',
    'Thu nhập khác'
);
