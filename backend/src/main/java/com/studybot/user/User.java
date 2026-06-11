package com.studybot.user;

import jakarta.persistence.*;
import lombok.Getter;
import lombok.Setter;
import lombok.NoArgsConstructor;
import lombok.AllArgsConstructor;
import lombok.Builder;

import java.time.LocalDateTime;

/**
 * Entity ánh xạ với bảng "users" trong MySQL.
 * Mỗi object User = 1 dòng trong bảng users.
 */
@Entity
@Table(name = "users")
@Getter @Setter
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class User {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(name = "telegram_id", nullable = false, unique = true)
    private Long telegramId;               // Telegram chat_id

    @Column(name = "username", length = 100)
    private String username;               // @username Telegram (có thể null)

    @Column(name = "full_name", nullable = false, length = 255)
    private String fullName;               // Tên hiển thị

    @Builder.Default
    @Column(name = "language_code", length = 10)
    private String languageCode = "vi";

    @Builder.Default
    @Column(name = "timezone", length = 50)
    private String timezone = "Asia/Ho_Chi_Minh";

    @Builder.Default
    @Column(name = "is_active", nullable = false)
    private Boolean isActive = true;

    @Column(name = "created_at", nullable = false, updatable = false)
    private LocalDateTime createdAt;

    @Column(name = "updated_at", nullable = false)
    private LocalDateTime updatedAt;

    // Quan hệ 1-1: 1 user có 1 bộ cài đặt
    // cascade = ALL → xóa user thì xóa settings theo
    // fetch = LAZY  → chỉ load settings khi thực sự cần (tối ưu hiệu năng)
    @OneToOne(mappedBy = "user", cascade = CascadeType.ALL, fetch = FetchType.LAZY)
    private UserSettings settings;

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
