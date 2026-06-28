package com.studybot.expense;

import com.studybot.user.User;
import com.studybot.user.UserRepository;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.math.BigDecimal;
import java.time.LocalDate;
import java.time.LocalDateTime;
import java.time.LocalTime;
import java.util.ArrayList;
import java.util.List;

/**
 * Service xử lý chi tiêu cá nhân.
 *
 * Chức năng:
 *  1. Thêm giao dịch (nhập tay hoặc từ kết quả AI scan)
 *  2. Lịch sử giao dịch
 *  3. Báo cáo tháng (tổng chi, tổng thu, theo danh mục)
 *  4. Lấy danh sách danh mục
 */
@Service
@RequiredArgsConstructor
@Slf4j
public class ExpenseService {

    private static final String OTHER_CATEGORY_NAME = "Khác";
    private static final String OTHER_CATEGORY_ICON = "📦";

    private final UserRepository              userRepository;
    private final ExpenseRepository           expenseRepository;
    private final ExpenseCategoryRepository   categoryRepository;

    // ═══════════════════════════════════════════════════════════
    //  DTO nội bộ
    // ═══════════════════════════════════════════════════════════

    public record AddExpenseRequest(
            Long     telegramId,
            String   type,          // "EXPENSE" | "INCOME"
            BigDecimal amount,
            Integer  categoryId,
            String   categoryName,  // dùng khi không có categoryId (auto-match)
            String   note,
            String   imageFileId,   // Telegram file_id nếu scan ảnh
            BigDecimal aiConfidence // null nếu nhập tay
    ) {}

    public record ExpenseResponse(
            Long        id,
            String      type,
            BigDecimal  amount,
            String      categoryName,
            String      categoryIcon,
            String      note,
            LocalDateTime transactionAt,
            String      source,
            BigDecimal  aiConfidence
    ) {}

    public record CategoryItem(Integer id, String name, String icon, String type) {}

    public record MonthlyReport(
            int    month,
            int    year,
            BigDecimal totalExpense,
            BigDecimal totalIncome,
            BigDecimal remaining,
            List<CategoryStat> categories
    ) {}

    public record CategoryStat(
            Integer    categoryId,
            String     categoryName,
            String     categoryIcon,
            BigDecimal amount,
            int        transactionCount
    ) {}

    // ═══════════════════════════════════════════════════════════
    //  1. Thêm giao dịch
    // ═══════════════════════════════════════════════════════════

    /**
     * Thêm giao dịch thu/chi mới.
     * Thêm giao dịch thu/chi mới. Tự động match danh mục nếu chỉ có tên.
     */
    @Transactional
    public ExpenseResponse addExpense(AddExpenseRequest req) {
        User user = getUser(req.telegramId());

        if (req.amount() == null || req.amount().compareTo(BigDecimal.ZERO) <= 0) {
            throw new IllegalArgumentException("Số tiền phải lớn hơn 0");
        }

        // Tìm danh mục
        ExpenseCategory category = resolveCategory(user, req.categoryId(), req.categoryName());

        Expense.ExpenseType type;
        try {
            type = Expense.ExpenseType.valueOf(req.type().toUpperCase());
        } catch (Exception e) {
            type = Expense.ExpenseType.EXPENSE;
        }

        Expense.ExpenseSource source = (req.imageFileId() != null && !req.imageFileId().isBlank())
                ? Expense.ExpenseSource.AI_SCAN
                : Expense.ExpenseSource.MANUAL;

        Expense expense = Expense.builder()
                .user(user)
                .category(category)
                .type(type)
                .amount(req.amount())
                .note(req.note())
                .transactionAt(LocalDateTime.now())
                .imageFileId(req.imageFileId())
                .source(source)
                .aiConfidence(req.aiConfidence())
                .build();

        expense = expenseRepository.save(expense);
        log.info("✅ Thêm giao dịch {} {}đ [{}] cho user {}",
                type, req.amount(), category.getName(), req.telegramId());

        return toResponse(expense);
    }

    // ═══════════════════════════════════════════════════════════
    //  2. Lịch sử giao dịch
    // ═══════════════════════════════════════════════════════════

    /**
     * Lấy lịch sử giao dịch theo period.
     * @param period "today" | "week" | "month" (mặc định: month)
     */
    @Transactional(readOnly = true)
    public List<ExpenseResponse> getHistory(Long telegramId, String period, int limit) {
        User user = getUser(telegramId);
        LocalDateTime now = LocalDateTime.now();

        LocalDateTime from = switch (period.toLowerCase()) {
            case "today" -> now.with(LocalTime.MIDNIGHT);
            case "week"  -> now.minusDays(7);
            case "year"  -> now.withDayOfYear(1).with(LocalTime.MIDNIGHT);
            case "all"   -> LocalDateTime.of(2000, 1, 1, 0, 0);
            default      -> now.withDayOfMonth(1).with(LocalTime.MIDNIGHT);
        };

        List<Expense> expenses = expenseRepository.findByUserAndPeriod(user, from, now);
        if (limit > 0 && expenses.size() > limit) {
            expenses = expenses.subList(0, limit);
        }
        return expenses.stream().map(this::toResponse).toList();
    }

    // ═══════════════════════════════════════════════════════════
    //  3. Báo cáo tháng
    // ═══════════════════════════════════════════════════════════

    @Transactional(readOnly = true)
    public MonthlyReport getMonthlyReport(Long telegramId, Integer month, Integer year) {
        User user = getUser(telegramId);
        LocalDate now = LocalDate.now();
        int m = (month != null) ? month : now.getMonthValue();
        int y = (year  != null) ? year  : now.getYear();

        BigDecimal totalExpense = nullSafe(expenseRepository.sumByType(user, Expense.ExpenseType.EXPENSE, m, y));
        BigDecimal totalIncome  = nullSafe(expenseRepository.sumByType(user, Expense.ExpenseType.INCOME,  m, y));
        BigDecimal remaining    = totalIncome.subtract(totalExpense);

        // Tổng chi theo từng danh mục
        List<Object[]> byCat = expenseRepository.sumByCategory(user, m, y);

        List<CategoryStat> stats = new ArrayList<>();
        for (Object[] row : byCat) {
            Integer catId  = (Integer) row[0];
            BigDecimal amt = (BigDecimal) row[1];
            categoryRepository.findById(catId).ifPresent(cat ->
                stats.add(new CategoryStat(catId, cat.getName(), cat.getIcon(), amt, 0))
            );
        }
        // Sort giảm dần theo số tiền
        stats.sort((a, b) -> b.amount().compareTo(a.amount()));

        return new MonthlyReport(m, y, totalExpense, totalIncome, remaining, stats);
    }

    // ═══════════════════════════════════════════════════════════
    //  4. Danh mục
    // ═══════════════════════════════════════════════════════════

    @Transactional
    public List<CategoryItem> getCategories(Long telegramId) {
        User user = getUser(telegramId);
        ensureOtherCategory(user);
        return categoryRepository.findByUserAndIsActiveTrue(user).stream()
                .map(c -> new CategoryItem(c.getId(), c.getName(), c.getIcon(),
                        c.getType() != null ? c.getType().name() : "EXPENSE"))
                .toList();
    }

    @Transactional
    public CategoryItem addCategory(Long telegramId, String name, String icon, String type) {
        User user = getUser(telegramId);
        ExpenseCategory.CategoryType catType;
        try {
            catType = ExpenseCategory.CategoryType.valueOf(type.toUpperCase());
        } catch (Exception e) {
            catType = ExpenseCategory.CategoryType.EXPENSE;
        }
        ExpenseCategory cat = ExpenseCategory.builder()
                .user(user)
                .name(name)
                .icon(icon)
                .type(catType)
                .isDefault(false)
                .isActive(true)
                .build();
        cat = categoryRepository.save(cat);
        log.info("✅ User {} tạo danh mục mới: {}", telegramId, name);
        return new CategoryItem(cat.getId(), cat.getName(), cat.getIcon(),
                cat.getType() != null ? cat.getType().name() : "EXPENSE");
    }

    @Transactional
    public CategoryItem updateCategory(Long telegramId, Integer categoryId, String name, String icon) {
        User user = getUser(telegramId);
        ExpenseCategory cat = categoryRepository.findById(categoryId)
                .orElseThrow(() -> new IllegalArgumentException("Danh mục không tồn tại: " + categoryId));
        if (cat.getUser() == null || !cat.getUser().getId().equals(user.getId())) {
            throw new IllegalArgumentException("Bạn không có quyền sửa danh mục này.");
        }
        if (Boolean.TRUE.equals(cat.getIsDefault())) {
            throw new IllegalArgumentException("Không thể sửa danh mục mặc định.");
        }
        if (name != null && !name.isBlank()) {
            cat.setName(name.trim());
        }
        if (icon != null && !icon.isBlank()) {
            cat.setIcon(icon.trim());
        }
        cat = categoryRepository.save(cat);
        log.info("✅ User {} sửa danh mục: id={}, name={}, icon={}", telegramId, categoryId, name, icon);
        return new CategoryItem(cat.getId(), cat.getName(), cat.getIcon(),
                cat.getType() != null ? cat.getType().name() : "EXPENSE");
    }

    @Transactional
    public void deleteCategory(Long telegramId, Integer categoryId) {
        User user = getUser(telegramId);
        ExpenseCategory cat = categoryRepository.findById(categoryId)
                .orElseThrow(() -> new IllegalArgumentException("Danh mục không tồn tại: " + categoryId));
        if (cat.getIsDefault()) {
            throw new IllegalArgumentException("Không thể xóa danh mục hệ thống mặc định.");
        }
        if (cat.getUser() == null || !cat.getUser().getId().equals(user.getId())) {
            throw new IllegalArgumentException("Bạn không có quyền xóa danh mục này.");
        }
        cat.setIsActive(false);   // soft delete
        categoryRepository.save(cat);
    }

    // ═══════════════════════════════════════════════════════════
    //  6. Xóa giao dịch
    // ═══════════════════════════════════════════════════════════

    @Transactional
    public void deleteExpense(Long telegramId, Long expenseId) {
        Expense expense = expenseRepository.findById(expenseId)
                .orElseThrow(() -> new IllegalArgumentException("Không tìm thấy giao dịch: " + expenseId));
        User user = getUser(telegramId);
        if (!expense.getUser().getId().equals(user.getId())) {
            throw new IllegalArgumentException("Bạn không có quyền xóa giao dịch này.");
        }
        expenseRepository.delete(expense);
    }

    @Transactional
    public ExpenseResponse updateExpense(Long telegramId, Long expenseId, BigDecimal amount,
                                          String categoryName, String note) {
        Expense expense = expenseRepository.findById(expenseId)
                .orElseThrow(() -> new IllegalArgumentException("Không tìm thấy giao dịch: " + expenseId));
        User user = getUser(telegramId);
        if (!expense.getUser().getId().equals(user.getId())) {
            throw new IllegalArgumentException("Bạn không có quyền sửa giao dịch này.");
        }
        if (amount != null) {
            if (amount.compareTo(BigDecimal.ZERO) <= 0) {
                throw new IllegalArgumentException("Số tiền phải lớn hơn 0");
            }
            expense.setAmount(amount);
        }
        if (categoryName != null && !categoryName.isBlank()) {
            expense.setCategory(resolveCategory(user, null, categoryName));
        }
        if (note != null) {
            expense.setNote(note.isBlank() ? null : note.trim());
        }
        return toResponse(expenseRepository.save(expense));
    }

    // ═══════════════════════════════════════════════════════════
    //  Private helpers
    // ═══════════════════════════════════════════════════════════

    private User getUser(Long telegramId) {
        return userRepository.findByTelegramId(telegramId)
                .orElseThrow(() -> new RuntimeException("User chưa đăng ký. Dùng /start trước."));
    }

    private ExpenseCategory resolveCategory(User user, Integer categoryId, String categoryName) {
        if (categoryId != null) {
            ExpenseCategory category = categoryRepository.findById(categoryId)
                    .orElseThrow(() -> new IllegalArgumentException("Danh mục không hợp lệ: " + categoryId));
            if (category.getUser() == null || !category.getUser().getId().equals(user.getId()) || !Boolean.TRUE.equals(category.getIsActive())) {
                throw new IllegalArgumentException("Danh mục không hợp lệ: " + categoryId);
            }
            return category;
        }

        if (categoryName != null && !categoryName.isBlank()) {
            List<ExpenseCategory> matches = categoryRepository.searchByNameForUser(categoryName, user).stream()
                    .toList();
            if (!matches.isEmpty()) return matches.get(0);
        }
        return ensureOtherCategory(user);
    }

    private ExpenseCategory ensureOtherCategory(User user) {
        Optional<ExpenseCategory> existing = categoryRepository.findByUser(user).stream()
                .filter(c -> OTHER_CATEGORY_NAME.equalsIgnoreCase(c.getName()))
                .findFirst();
        if (existing.isPresent()) {
            ExpenseCategory category = existing.get();
            boolean changed = false;
            if (!Boolean.TRUE.equals(category.getIsActive())) {
                category.setIsActive(true);
                changed = true;
            }
            if (!Boolean.TRUE.equals(category.getIsDefault())) {
                category.setIsDefault(true);
                changed = true;
            }
            if (category.getIcon() == null || category.getIcon().isBlank()) {
                category.setIcon(OTHER_CATEGORY_ICON);
                changed = true;
            }
            if (category.getType() == null) {
                category.setType(ExpenseCategory.CategoryType.EXPENSE);
                changed = true;
            }
            return changed ? categoryRepository.save(category) : category;
        }

        ExpenseCategory category = ExpenseCategory.builder()
                .user(user)
                .name(OTHER_CATEGORY_NAME)
                .icon(OTHER_CATEGORY_ICON)
                .type(ExpenseCategory.CategoryType.EXPENSE)
                .isDefault(true)
                .isActive(true)
                .sortOrder(0)
                .build();
        return categoryRepository.save(category);
    }

    private ExpenseResponse toResponse(Expense e) {
        return new ExpenseResponse(
                e.getId(),
                e.getType().name(),
                e.getAmount(),
                e.getCategory().getName(),
                e.getCategory().getIcon(),
                e.getNote(),
                e.getTransactionAt(),
                e.getSource().name(),
                e.getAiConfidence()
        );
    }

    private BigDecimal nullSafe(BigDecimal val) {
        return val != null ? val : BigDecimal.ZERO;
    }
}
