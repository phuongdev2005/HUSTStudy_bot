package com.studybot.expense;

import jakarta.persistence.*;
import lombok.*;
import com.studybot.user.User;

/**
 * Danh mục thu/chi (Ăn uống, Di chuyển, Học phí & Sách, ...).
 * Ánh xạ đến bảng `expense_categories`.
 *
 * user_id = NULL  → danh mục mặc định hệ thống (seed ở V2)
 * user_id có giá trị → danh mục do user tự tạo
 */
@Entity
@Table(name = "expense_categories")
@Getter @Setter
@NoArgsConstructor @AllArgsConstructor
@Builder
public class ExpenseCategory {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Integer id;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "user_id")   // nullable — null = danh mục hệ thống
    private User user;

    @Column(name = "name", nullable = false, length = 100)
    private String name;

    @Column(name = "icon", length = 10)
    private String icon;

    @Enumerated(EnumType.STRING)
    @Column(name = "type", length = 10)
    @Builder.Default
    private CategoryType type = CategoryType.EXPENSE;

    @Column(name = "is_default", nullable = false)
    @Builder.Default
    private Boolean isDefault = false;

    @Column(name = "is_active", nullable = false)
    @Builder.Default
    private Boolean isActive = true;

    @Column(name = "sort_order")
    @Builder.Default
    private Integer sortOrder = 0;

    public enum CategoryType {
        EXPENSE, INCOME, BOTH
    }
}
