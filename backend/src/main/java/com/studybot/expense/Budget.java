package com.studybot.expense;

import jakarta.persistence.*;
import lombok.*;
import com.studybot.user.User;

import java.math.BigDecimal;
import java.time.LocalDateTime;

/**
 * Ngân sách theo danh mục mỗi tháng.
 * Dùng để cảnh báo khi chi tiêu đạt 80% / 100% hạn mức.
 */
@Entity
@Table(name = "budgets",
       uniqueConstraints = @UniqueConstraint(columnNames = {"user_id", "category_id", "month", "year"}))
@Getter @Setter
@NoArgsConstructor @AllArgsConstructor
@Builder
public class Budget {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "user_id", nullable = false)
    private User user;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "category_id", nullable = false)
    private ExpenseCategory category;

    @Column(name = "month", nullable = false)
    private Integer month;   // 1–12

    @Column(name = "year", nullable = false)
    private Integer year;

    /** Hạn mức tháng (VNĐ) — cột `amount` trong DB */
    @Column(name = "amount", nullable = false, precision = 15, scale = 2)
    private BigDecimal amount;

    /** Ngưỡng cảnh báo, mặc định 0.80 (80%) */
    @Column(name = "warn_threshold", precision = 4, scale = 2)
    @Builder.Default
    private BigDecimal warnThreshold = new BigDecimal("0.80");

    @Column(name = "is_notified_80")
    @Builder.Default
    private Boolean isNotified80 = false;

    @Column(name = "is_notified_100")
    @Builder.Default
    private Boolean isNotified100 = false;

    @Column(name = "created_at", nullable = false, updatable = false)
    private LocalDateTime createdAt;

    @Column(name = "updated_at", nullable = false)
    private LocalDateTime updatedAt;

    @PrePersist
    protected void onCreate() {
        createdAt = LocalDateTime.now();
        updatedAt = LocalDateTime.now();
    }

    @PreUpdate
    protected void onUpdate() {
        updatedAt = LocalDateTime.now();
    }
}
