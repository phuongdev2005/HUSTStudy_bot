package com.studybot.vocabulary;

import com.studybot.user.User;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;

import java.time.LocalDateTime;
import java.util.List;
import java.util.Optional;

@Repository
public interface WordRepository extends JpaRepository<Word, Long> {

    /** Lấy từ tiếp theo cần ôn (nextReviewAt nhỏ nhất, chưa tới tương lai). */
    @Query("""
        SELECT w FROM Word w
        WHERE w.user = :user AND w.nextReviewAt <= :now
        ORDER BY w.nextReviewAt ASC
        LIMIT 1
    """)
    Optional<Word> findNextForReview(@Param("user") User user,
                                     @Param("now")  LocalDateTime now);

    /** Lấy tất cả từ của user, sắp xếp theo ngày thêm mới nhất. */
    List<Word> findByUserOrderByCreatedAtDesc(User user);

    /** Kiểm tra từ đã tồn tại chưa (không phân biệt hoa thường). */
    boolean existsByUserAndWordIgnoreCase(User user, String word);
}
