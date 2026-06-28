package com.studybot.expense;

import com.studybot.user.User;
import com.studybot.user.UserRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.math.BigDecimal;
import java.util.List;
import java.util.Map;

/**
 * REST Controller cho module Quản lý Chi tiêu.
 *
 * Base URL: /api/expense
 *
 * Endpoints:
 *   POST   /api/expense/add              → Thêm giao dịch (nhập tay)
 *   POST   /api/expense/scan             → Scan ảnh hóa đơn bằng Groq AI
 *   POST   /api/expense/confirm-scan     → Xác nhận và lưu kết quả AI scan
 *   GET    /api/expense/history          → Lịch sử giao dịch
 *   GET    /api/expense/report           → Báo cáo tháng
 *   GET    /api/expense/categories       → Danh sách danh mục
 *   POST   /api/expense/budget           → Đặt hạn mức
 *   GET    /api/expense/budget           → Xem hạn mức tháng
 *   DELETE /api/expense/{id}             → Xóa giao dịch
 */
@RestController
@RequestMapping("/expense")
@RequiredArgsConstructor
public class ExpenseController {

    private final ExpenseService       expenseService;
    private final GroqKeyService       groqKeyService;
    private final UserRepository       userRepository;

    // ─────────────────────────────────────────────────────────────
    //  1. Thêm giao dịch nhập tay
    //
    //  POST /api/expense/add
    //  Body: { telegramId, type, amount, categoryId?, categoryName?, note? }
    // ─────────────────────────────────────────────────────────────
    @PostMapping("/add")
    public ResponseEntity<ExpenseService.ExpenseResponse> addExpense(
            @RequestBody Map<String, Object> body) {

        ExpenseService.AddExpenseRequest req = new ExpenseService.AddExpenseRequest(
                getLong(body, "telegramId"),
                getString(body, "type", "EXPENSE"),
                getBigDecimal(body, "amount"),
                getInt(body, "categoryId"),
                getString(body, "categoryName", null),
                getString(body, "note", null),
                null,   // imageFileId — null vì nhập tay
                null    // aiConfidence
        );

        ExpenseService.ExpenseResponse result = expenseService.addExpense(req);
        return ResponseEntity.status(201).body(result);
    }



    // ─────────────────────────────────────────────────────────────
    //  3. Xác nhận và lưu kết quả AI scan
    //
    //  POST /api/expense/confirm-scan
    //  Body: { telegramId, amount, categoryName, note, imageFileId, aiConfidence }
    // ─────────────────────────────────────────────────────────────
    @PostMapping("/confirm-scan")
    public ResponseEntity<ExpenseService.ExpenseResponse> confirmScan(
            @RequestBody Map<String, Object> body) {

        ExpenseService.AddExpenseRequest req = new ExpenseService.AddExpenseRequest(
                getLong(body, "telegramId"),
                getString(body, "type", "EXPENSE"),
                getBigDecimal(body, "amount"),
                null,
                getString(body, "categoryName", "Khác"),
                getString(body, "note", null),
                getString(body, "imageFileId", null),
                getBigDecimal(body, "aiConfidence")
        );

        ExpenseService.ExpenseResponse result = expenseService.addExpense(req);
        return ResponseEntity.status(201).body(result);
    }

    // ─────────────────────────────────────────────────────────────
    //  4. Lịch sử giao dịch
    //
    //  GET /api/expense/history?telegramId=xxx&period=month&limit=20
    // ─────────────────────────────────────────────────────────────
    @GetMapping("/history")
    public ResponseEntity<List<ExpenseService.ExpenseResponse>> getHistory(
            @RequestParam Long    telegramId,
            @RequestParam(defaultValue = "month") String period,
            @RequestParam(defaultValue = "20")    int    limit) {

        return ResponseEntity.ok(expenseService.getHistory(telegramId, period, limit));
    }

    // ─────────────────────────────────────────────────────────────
    //  5. Báo cáo tháng
    //
    //  GET /api/expense/report?telegramId=xxx&month=6&year=2026
    // ─────────────────────────────────────────────────────────────
    @GetMapping("/report")
    public ResponseEntity<ExpenseService.MonthlyReport> getReport(
            @RequestParam Long    telegramId,
            @RequestParam(required = false) Integer month,
            @RequestParam(required = false) Integer year) {

        return ResponseEntity.ok(expenseService.getMonthlyReport(telegramId, month, year));
    }

    // ─────────────────────────────────────────────────────────────
    //  6. Danh sách danh mục
    //
    //  GET /api/expense/categories?telegramId=xxx
    // ─────────────────────────────────────────────────────────────
    @GetMapping("/categories")
    public ResponseEntity<List<ExpenseService.CategoryItem>> getCategories(
            @RequestParam Long telegramId) {
        return ResponseEntity.ok(expenseService.getCategories(telegramId));
    }

    // ─────────────────────────────────────────────────────────────
    //  6b. Tạo danh mục riêng
    //
    //  POST /api/expense/categories
    //  Body: { telegramId, name, icon?, type? }
    // ─────────────────────────────────────────────────────────────
    @PostMapping("/categories")
    public ResponseEntity<Map<String, Object>> addCategory(
            @RequestBody Map<String, Object> body) {
        Long   telegramId = getLong(body, "telegramId");
        String name       = getString(body, "name", null);
        String icon       = getString(body, "icon", "📦");
        String type       = getString(body, "type", "EXPENSE");

        if (name == null || name.isBlank())
            throw new IllegalArgumentException("Tên danh mục không được để trống");

        ExpenseService.CategoryItem cat = expenseService.addCategory(telegramId, name.trim(), icon, type);
        return ResponseEntity.status(201).body(Map.of(
                "id",      cat.id(),
                "name",    cat.name(),
                "icon",    cat.icon() != null ? cat.icon() : "",
                "type",    cat.type(),
                "message", "✅ Đã thêm danh mục: " + cat.name()
        ));
    }

    // ─────────────────────────────────────────────────────────────
    //  6c. Xóa danh mục riêng (chỉ của user)
    //
    //  DELETE /api/expense/categories/{id}?telegramId=xxx
    // ─────────────────────────────────────────────────────────────
    @DeleteMapping("/categories/{id}")
    public ResponseEntity<Map<String, String>> deleteCategory(
            @PathVariable Integer id,
            @RequestParam Long telegramId) {
        expenseService.deleteCategory(telegramId, id);
        return ResponseEntity.ok(Map.of("message", "✅ Đã xóa danh mục"));
    }

    // ─────────────────────────────────────────────────────────────
    //  6d. Sửa danh mục riêng (tên, icon)
    //
    //  PUT /api/expense/categories/{id}
    //  Body: { telegramId, name?, icon? }
    // ─────────────────────────────────────────────────────────────
    @PutMapping("/categories/{id}")
    public ResponseEntity<Map<String, Object>> updateCategory(
            @PathVariable Integer id,
            @RequestBody Map<String, Object> body) {
        Long   telegramId = getLong(body, "telegramId");
        String name       = getString(body, "name", null);
        String icon       = getString(body, "icon", null);

        ExpenseService.CategoryItem cat = expenseService.updateCategory(telegramId, id, name, icon);
        return ResponseEntity.ok(Map.of(
                "id",      cat.id(),
                "name",    cat.name(),
                "icon",    cat.icon() != null ? cat.icon() : "",
                "type",    cat.type(),
                "message", "✅ Đã cập nhật danh mục: " + cat.name()
        ));
    }

    // ─────────────────────────────────────────────────────────────
    //  7. Đặt hạn mức ngân sách
    //
    //  POST /api/expense/budget
    //  Body: { telegramId, categoryId, amount, month?, year? }
    // ─────────────────────────────────────────────────────────────
    @PostMapping("/budget")
    public ResponseEntity<Map<String, Object>> setBudget(
            @RequestBody Map<String, Object> body) {

        Budget budget = expenseService.setBudget(
                getLong(body, "telegramId"),
                getInt(body, "categoryId"),
                getBigDecimal(body, "amount"),
                getInt(body, "month"),
                getInt(body, "year")
        );

        return ResponseEntity.status(201).body(Map.of(
                "id",       budget.getId(),
                "category", budget.getCategory().getName(),
                "amount",   budget.getAmount(),
                "month",    budget.getMonth(),
                "year",     budget.getYear(),
                "message",  "✅ Đã đặt hạn mức " + formatVnd(budget.getAmount()) +
                            " cho " + budget.getCategory().getName()
        ));
    }

    // ─────────────────────────────────────────────────────────────
    //  8. Xem hạn mức tháng
    //
    //  GET /api/expense/budget?telegramId=xxx&month=6&year=2026
    // ─────────────────────────────────────────────────────────────
    @GetMapping("/budget")
    public ResponseEntity<List<Map<String, Object>>> getBudgets(
            @RequestParam Long    telegramId,
            @RequestParam(required = false) Integer month,
            @RequestParam(required = false) Integer year) {

        List<Budget> budgets = expenseService.getBudgets(telegramId, month, year);
        List<Map<String, Object>> result = budgets.stream().map(b -> Map.<String, Object>of(
                "id",           b.getId(),
                "category",     b.getCategory().getName(),
                "icon",         b.getCategory().getIcon() != null ? b.getCategory().getIcon() : "",
                "amount",       b.getAmount(),
                "month",        b.getMonth(),
                "year",         b.getYear(),
                "warnThreshold",b.getWarnThreshold()
        )).toList();

        return ResponseEntity.ok(result);
    }

    // ─────────────────────────────────────────────────────────────
    //  9. Xóa giao dịch
    //
    //  DELETE /api/expense/{id}?telegramId=xxx
    // ─────────────────────────────────────────────────────────────
    @DeleteMapping("/{id}")
    public ResponseEntity<Map<String, String>> deleteExpense(
            @PathVariable Long id,
            @RequestParam Long telegramId) {

        expenseService.deleteExpense(telegramId, id);
        return ResponseEntity.ok(Map.of("message", "✅ Đã xóa giao dịch #" + id));
    }

    // ────────────────────────────────────────────────────────────
    // 10. Cài Groq API Key riêng
    //
    //  POST /api/expense/setkey
    //  Body: { telegramId, apiKey }  (apiKey = null để xóa key)
    // ────────────────────────────────────────────────────────────
    //  PUT /api/expense/{id}
    //  Body: { telegramId, amount?, categoryName?, note? }
    @PutMapping("/{id}")
    public ResponseEntity<ExpenseService.ExpenseResponse> updateExpense(
            @PathVariable Long id,
            @RequestBody Map<String, Object> body) {

        ExpenseService.ExpenseResponse result = expenseService.updateExpense(
                getLong(body, "telegramId"),
                id,
                getBigDecimal(body, "amount"),
                getString(body, "categoryName", null),
                getString(body, "note", null)
        );
        return ResponseEntity.ok(result);
    }

    @PostMapping("/setkey")
    public ResponseEntity<Map<String, String>> setGroqKey(
            @RequestBody Map<String, Object> body) {
        User user = getUser(getLong(body, "telegramId"));
        String apiKey = getString(body, "apiKey", null);
        String message = groqKeyService.setUserKey(user, apiKey);
        return ResponseEntity.ok(Map.of("message", message));
    }

    // ────────────────────────────────────────────────────────────
    // 11. Xem trạng thái quota / key
    //
    //  GET /api/expense/keystatus?telegramId=xxx
    // ────────────────────────────────────────────────────────────
    @GetMapping("/keystatus")
    public ResponseEntity<Map<String, Object>> getKeyStatus(
            @RequestParam Long telegramId) {
        User user = getUser(telegramId);
        GroqKeyService.KeyStatus status = groqKeyService.getStatus(user);

        String message;
        if (status.hasOwnKey()) {
            message = "✅ Bạn đang dùng Groq API Key riêng → không giới hạn số lần scan.";
        } else {
            message = String.format(
                "📊 Scan AI miễn phí: đã dùng %d/%d lượt hôm nay.\n" +
                "Lấy key riêng miễn phí tại https://console.groq.com/keys\n" +
                "Cài vào bot: /setkey <key>",
                status.usedToday(), GroqKeyService.FREE_DAILY_LIMIT);
        }

        return ResponseEntity.ok(Map.of(
                "hasOwnKey",   status.hasOwnKey(),
                "apiKey",      status.userKey() != null ? status.userKey() : "",
                "usedToday",   status.usedToday(),
                "remaining",   status.remaining(),
                "isUnlimited", status.isUnlimited(),
                "freeLimit",   GroqKeyService.FREE_DAILY_LIMIT,
                "message",     message
        ));
    }


    // ═══════════════════════════════════════════════════════════
    //  Parse helpers
    // ═══════════════════════════════════════════════════════════

    private Long getLong(Map<String, Object> body, String key) {
        Object v = body.get(key);
        if (v == null) throw new IllegalArgumentException("Thiếu field: " + key);
        return ((Number) v).longValue();
    }

    private Integer getInt(Map<String, Object> body, String key) {
        Object v = body.get(key);
        return v != null ? ((Number) v).intValue() : null;
    }

    private BigDecimal getBigDecimal(Map<String, Object> body, String key) {
        Object v = body.get(key);
        if (v == null) return null;
        return new BigDecimal(v.toString());
    }

    private String getString(Map<String, Object> body, String key, String defaultVal) {
        Object v = body.get(key);
        return v != null ? v.toString() : defaultVal;
    }

    private String formatVnd(BigDecimal amount) {
        return String.format("%,.0f đ", amount);
    }

    private com.studybot.user.User getUser(Long telegramId) {
        return userRepository.findByTelegramId(telegramId)
                .orElseThrow(() -> new RuntimeException("User chưa đăng ký. Dùng /start trước."));
    }
}
