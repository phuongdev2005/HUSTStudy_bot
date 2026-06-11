package com.studybot.deadline;

import jakarta.persistence.*;
import lombok.*;
import com.studybot.user.User;

import java.time.LocalDate;
import java.time.LocalDateTime;

/**
 * Entity deadline bài tập / nhiệm vụ học tập.
 */
@Entity
@Table(name = "deadlines")
@Getter @Setter
@NoArgsConstructor @AllArgsConstructor
@Builder
public class Deadline {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "user_id", nullable = false)
    private User user;

    @Column(name = "title", nullable = false, length = 300)
    private String title;             // Tên bài tập / nhiệm vụ

    @Column(name = "subject", length = 200)
    private String subject;           // Môn học liên quan

    @Column(name = "due_date", nullable = false)
    private LocalDate dueDate;        // Hạn nộp

    @Column(name = "note", columnDefinition = "TEXT")
    private String note;              // Ghi chú thêm

    @Builder.Default
    @Column(name = "is_done", nullable = false)
    private Boolean isDone = false;   // Đã hoàn thành chưa

    @Column(name = "created_at", nullable = false, updatable = false)
    private LocalDateTime createdAt;

    @PrePersist
    protected void onCreate() {
        createdAt = LocalDateTime.now();
    }
}
