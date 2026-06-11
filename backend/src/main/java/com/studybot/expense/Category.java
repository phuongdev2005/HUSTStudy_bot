package com.studybot.expense;

import jakarta.persistence.*;
import lombok.*;

/**
 * Danh mục chi tiêu (Ăn uống, Di chuyển, Học phí, ...).
 */
@Entity
@Table(name = "categories")
@Getter @Setter
@NoArgsConstructor @AllArgsConstructor
@Builder
public class Category {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(name = "name", nullable = false, length = 100)
    private String name;              // Tên danh mục

    @Column(name = "icon", length = 10)
    private String icon;              // Emoji icon (vd: "🍜")

    @Column(name = "description", length = 300)
    private String description;

    /**
     * true = danh mục mặc định hệ thống (Ăn uống, Di chuyển, ...)
     * false = danh mục tự tạo của user
     */
    @Builder.Default
    @Column(name = "is_default", nullable = false)
    private Boolean isDefault = false;
}
