package com.studybot.vocabulary;

import jakarta.persistence.*;
import lombok.*;
import com.studybot.user.User;

import java.time.LocalDateTime;

/**
 * Entity kết quả mỗi lần ôn tập từ vựng.
 * Dùng để thống kê tiến độ học của user.
 */
@Entity
@Table(name = "quiz_results")
@Getter @Setter
@NoArgsConstructor @AllArgsConstructor
@Builder
public class QuizResult {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "user_id", nullable = false)
    private User user;

    @Column(name = "total_questions", nullable = false)
    private Integer totalQuestions;

    @Column(name = "correct_answers", nullable = false)
    private Integer correctAnswers;

    @Column(name = "wrong_answers", nullable = false)
    private Integer wrongAnswers;

    @Column(name = "score_percent", nullable = false)
    private Integer scorePercent;     // 0–100

    @Column(name = "played_at", nullable = false, updatable = false)
    private LocalDateTime playedAt;

    @PrePersist
    protected void onCreate() {
        playedAt = LocalDateTime.now();
    }
}
