package com.studybot.vocabulary;

import jakarta.persistence.*;
import lombok.*;
import com.studybot.user.User;

import java.time.LocalDateTime;

/**
 * Entity từ vựng tiếng Anh của user.
 */
@Entity
@Table(name = "words")
@Getter @Setter
@NoArgsConstructor @AllArgsConstructor
@Builder
public class Word {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "user_id", nullable = false)
    private User user;

    @Column(name = "word", nullable = false, length = 200)
    private String word;              // Từ tiếng Anh (vd: "apple")

    @Column(name = "meaning", nullable = false, length = 500)
    private String meaning;           // Nghĩa tiếng Việt (vd: "quả táo")

    @Column(name = "example", columnDefinition = "TEXT")
    private String example;           // Câu ví dụ

    @Column(name = "pronunciation", length = 200)
    private String pronunciation;     // Phiên âm IPA

    /**
     * Cấp độ học theo Spaced Repetition (0 = mới, tăng dần khi trả lời đúng).
     */
    @Builder.Default
    @Column(name = "level", nullable = false)
    private Integer level = 0;

    @Column(name = "next_review_at")
    private LocalDateTime nextReviewAt; // Thời điểm ôn tập tiếp theo

    @Column(name = "created_at", nullable = false, updatable = false)
    private LocalDateTime createdAt;

    @PrePersist
    protected void onCreate() {
        createdAt = LocalDateTime.now();
        if (nextReviewAt == null) nextReviewAt = LocalDateTime.now();
    }
}
