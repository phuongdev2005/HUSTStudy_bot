package com.studybot.expense;

import jakarta.persistence.*;
import lombok.*;
import com.studybot.user.User;

import java.math.BigDecimal;

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
    private Category category;

    @Column(name = "limit_amount", nullable = false, precision = 15, scale = 0)
    private BigDecimal limitAmount;   // Hạn mức tháng (VNĐ)

    @Column(name = "month", nullable = false)
    private Integer month;            // 1–12

    @Column(name = "year", nullable = false)
    private Integer year;
}
