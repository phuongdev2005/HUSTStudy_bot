package com.studybot.schedule;

import com.studybot.user.User;
import jakarta.persistence.*;
import lombok.*;

import java.time.LocalDate;
import java.time.LocalDateTime;

/**
 * Entity ánh xạ bảng "daily_activities".
 *
 * Mỗi dòng = 1 khung giờ hoạt động trong ngày của user.
 * Ví dụ: 00:00–06:30 Ngủ, 06:30–07:00 Vệ sinh cá nhân, ...
 *
 * day_of_week = NULL  → hoạt động lặp lại mọi ngày (ăn, ngủ, vệ sinh)
 * day_of_week = 1–7   → hoạt động riêng ngày đó (lịch học, buổi tập...)
 *   1=T2, 2=T3, 3=T4, 4=T5, 5=T6, 6=T7, 7=CN
 */
@Entity
@Table(name = "daily_activities")
@Getter @Setter
@NoArgsConstructor @AllArgsConstructor
@Builder
public class DailyActivity {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "user_id", nullable = false)
    private User user;

    /**
     * Thứ trong tuần: NULL = mọi ngày, 1=T2 … 7=CN.
     */
    @Column(name = "day_of_week")
    private Integer dayOfWeek;

    @Column(name = "start_time", nullable = false, length = 5)
    private String startTime;           // HH:mm

    @Column(name = "end_time", nullable = false, length = 5)
    private String endTime;             // HH:mm

    @Column(name = "activity", nullable = false, length = 255)
    private String activity;            // Tên hoạt động

    @Column(name = "category", nullable = false, length = 50)
    private String category = "Khác";  // Danh mục

    /** Manual getter vì Lombok đôi khi bỏ qua field có default value. */
    public String getCategory() {
        return category != null ? category : "Khác";
    }

    @Column(name = "note", length = 500)
    private String note;                // Ghi chú (phòng, địa điểm...)

    @Column(name = "sort_order", nullable = false)
    private Integer sortOrder = 0;

    @Column(name = "date")
    private LocalDate date;

    @Column(name = "created_at", nullable = false, updatable = false)
    private LocalDateTime createdAt;

    @Column(name = "updated_at", nullable = false)
    private LocalDateTime updatedAt;

    @PrePersist
    protected void onCreate() {
        if (category == null) category = "Khác";
        if (sortOrder == null) sortOrder = 0;
        createdAt = LocalDateTime.now();
        updatedAt = LocalDateTime.now();
    }

    @PreUpdate
    protected void onUpdate() {
        updatedAt = LocalDateTime.now();
    }
}
