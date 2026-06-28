package com.studybot.deadline;

import com.studybot.user.User;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;

import java.util.List;

@Repository
public interface DeadlineRepository extends JpaRepository<Deadline, Long> {

    /** Lấy tất cả deadline chưa hoàn thành và chưa quá hạn của user, sắp xếp theo hạn nộp gần nhất. */
    @Query("""
        SELECT d FROM Deadline d
        WHERE d.user = :user AND d.isDone = false AND d.dueDate >= :today
        ORDER BY d.dueDate ASC
    """)
    List<Deadline> findPendingByUser(@Param("user") User user, @Param("today") java.time.LocalDate today);

    /** Lấy tất cả deadline (kể cả đã done) để xem lịch sử. */
    List<Deadline> findByUserOrderByDueDateAsc(User user);
}
