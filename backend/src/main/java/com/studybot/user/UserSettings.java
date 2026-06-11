package com.studybot.user;

import jakarta.persistence.*;
import lombok.*;

import java.time.LocalTime;
import java.time.LocalDateTime;

/**
 * Entity ánh xạ với bảng "user_settings".
 * Quan hệ 1-1 với User — mỗi user có đúng 1 bộ cài đặt.
 */
@Entity
@Table(name = "user_settings")
@Getter @Setter
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class UserSettings {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    // Quan hệ 1-1 với User
    // @JoinColumn: cột "user_id" trong bảng user_settings trỏ đến users.id
    @OneToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "user_id", nullable = false, unique = true)
    private User user;

    // ── Bật/tắt từng loại thông báo ──────────────────────────
    @Builder.Default
    @Column(name = "notify_class_remind")
    private Boolean notifyClassRemind = true;

    @Builder.Default
    @Column(name = "notify_deadline")
    private Boolean notifyDeadline = true;

    @Builder.Default
    @Column(name = "notify_exam")
    private Boolean notifyExam = true;

    @Builder.Default
    @Column(name = "notify_budget_warn")
    private Boolean notifyBudgetWarn = true;

    @Builder.Default
    @Column(name = "notify_daily_summary")
    private Boolean notifyDailySummary = true;

    // ── Thời gian và khoảng cách nhắc ────────────────────────
    @Builder.Default
    @Column(name = "daily_summary_time")
    private LocalTime dailySummaryTime = LocalTime.of(7, 0); // 07:00

    @Builder.Default
    @Column(name = "class_remind_before", columnDefinition = "SMALLINT")
    private Short classRemindBefore = 30;          // phút

    @Builder.Default
    @Column(name = "deadline_remind_before", columnDefinition = "SMALLINT")
    private Short deadlineRemindBefore = 1440;     // phút (1 ngày)

    @Builder.Default
    @Column(name = "exam_remind_before_days", columnDefinition = "TINYINT")
    private Short examRemindBeforeDays = 2;        // ngày

    @Column(name = "updated_at", nullable = false)
    private LocalDateTime updatedAt;

    @PrePersist
    @PreUpdate
    protected void onUpdate() {
        updatedAt = LocalDateTime.now();
    }
}
