package com.studybot.exam;

import jakarta.persistence.*;
import lombok.*;
import com.studybot.user.User;

import java.time.LocalDate;
import java.time.LocalTime;
import java.time.LocalDateTime;

/**
 * Entity lịch thi.
 * Lưu thông tin môn thi, phòng thi, thời gian thi.
 */
@Entity
@Table(name = "exams")
@Getter @Setter
@NoArgsConstructor @AllArgsConstructor
@Builder
public class Exam {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "user_id", nullable = false)
    private User user;

    @Column(name = "subject_name", nullable = false, length = 200)
    private String subject;           // Tên môn thi

    @Column(name = "exam_date", nullable = false)
    private LocalDate examDate;       // Ngày thi

    @Column(name = "start_time", nullable = false)
    private LocalTime startTime;      // Giờ bắt đầu (vd: 07:00)

    @Column(name = "duration_min")
    private Integer durationMinutes;  // Thời gian làm bài (phút)

    @Column(name = "room", length = 50)
    private String room;              // Phòng thi (vd: A305)

    @Column(name = "exam_type", length = 50)
    private String examType;          // Hình thức: Tự luận, Trắc nghiệm, Thực hành

    @Column(name = "note", columnDefinition = "TEXT")
    private String note;

    @Column(name = "created_at", nullable = false, updatable = false)
    private LocalDateTime createdAt;

    @PrePersist
    protected void onCreate() {
        createdAt = LocalDateTime.now();
    }
}
