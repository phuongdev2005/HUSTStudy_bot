package com.studybot.expense;

import jakarta.persistence.*;
import lombok.*;
import com.studybot.user.User;

import java.math.BigDecimal;
import java.time.LocalDateTime;

/**
 * Entity giao dịch thu/chi.
 */
@Entity
@Table(name = "transactions")
@Getter @Setter
@NoArgsConstructor @AllArgsConstructor
@Builder
public class Transaction {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "user_id", nullable = false)
    private User user;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "category_id")
    private Category category;

    /**
     * Loại giao dịch: EXPENSE (chi tiêu) hoặc INCOME (thu nhập)
     */
    @Enumerated(EnumType.STRING)
    @Column(name = "type", nullable = false, length = 10)
    private TransactionType type;

    @Column(name = "amount", nullable = false, precision = 15, scale = 0)
    private BigDecimal amount;        // Số tiền (VNĐ)

    @Column(name = "note", length = 500)
    private String note;              // Ghi chú (vd: "cơm trưa")

    @Column(name = "transacted_at", nullable = false)
    private LocalDateTime transactedAt; // Thời điểm giao dịch

    @Column(name = "created_at", nullable = false, updatable = false)
    private LocalDateTime createdAt;

    @PrePersist
    protected void onCreate() {
        createdAt = LocalDateTime.now();
        if (transactedAt == null) transactedAt = LocalDateTime.now();
    }

    public enum TransactionType {
        EXPENSE, INCOME
    }
}
