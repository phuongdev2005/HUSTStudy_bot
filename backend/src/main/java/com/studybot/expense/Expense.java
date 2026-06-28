package com.studybot.expense;

import jakarta.persistence.*;
import lombok.*;
import com.studybot.user.User;

import java.math.BigDecimal;
import java.time.LocalDateTime;

/**
 * Entity giao dịch thu/chi.
 * Ánh xạ đến bảng `expenses` trong DB.
 */
@Entity
@Table(name = "expenses")
@Getter @Setter
@NoArgsConstructor @AllArgsConstructor
@Builder
public class Expense {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "user_id", nullable = false)
    private User user;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "category_id", nullable = false)
    private ExpenseCategory category;

    /**
     * Loại giao dịch: EXPENSE (chi tiêu) hoặc INCOME (thu nhập)
     */
    @Enumerated(EnumType.STRING)
    @Column(name = "type", nullable = false, length = 10)
    private ExpenseType type;

    @Column(name = "amount", nullable = false, precision = 15, scale = 2)
    private BigDecimal amount;

    @Column(name = "note", length = 500)
    private String note;

    @Column(name = "transaction_at", nullable = false)
    private LocalDateTime transactionAt;

    // ── AI Scan fields ──────────────────────────────────────────

    /** Telegram file_id của ảnh hóa đơn gốc (null nếu nhập tay) */
    @Column(name = "image_file_id", length = 255)
    private String imageFileId;

    /** Nguồn gốc: MANUAL (nhập tay) hoặc AI_SCAN (quét ảnh Groq) */
    @Enumerated(EnumType.STRING)
    @Column(name = "source", nullable = false, length = 10)
    @Builder.Default
    private ExpenseSource source = ExpenseSource.MANUAL;

    /** Độ tin cậy của AI (0.00–1.00), null nếu nhập tay */
    @Column(name = "ai_confidence", precision = 3, scale = 2)
    private BigDecimal aiConfidence;

    @Column(name = "created_at", nullable = false, updatable = false)
    private LocalDateTime createdAt;

    @Column(name = "updated_at", nullable = false)
    private LocalDateTime updatedAt;

    @PrePersist
    protected void onCreate() {
        createdAt = LocalDateTime.now();
        updatedAt = LocalDateTime.now();
        if (transactionAt == null) transactionAt = LocalDateTime.now();
        if (source == null) source = ExpenseSource.MANUAL;
    }

    @PreUpdate
    protected void onUpdate() {
        updatedAt = LocalDateTime.now();
    }

    public enum ExpenseType {
        EXPENSE, INCOME
    }

    public enum ExpenseSource {
        MANUAL, AI_SCAN
    }
}
