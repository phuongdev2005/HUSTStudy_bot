package com.studybot.schedule;

import com.studybot.user.User;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;

import java.time.LocalDate;
import java.util.List;

/**
 * Repository cho bảng "daily_activities".
 */
@Repository
public interface DailyActivityRepository extends JpaRepository<DailyActivity, Long> {

    /**
     * Lấy lịch sinh hoạt theo ngày cụ thể.
     */
    @Query("""
            SELECT a FROM DailyActivity a
            WHERE a.user.id = :userId
              AND a.date = :date
            ORDER BY a.startTime, a.sortOrder
            """)
    List<DailyActivity> findByUserIdAndDate(
            @Param("userId") Long userId,
            @Param("date") LocalDate date);

    /**
     * Lấy lịch sinh hoạt hàng tuần lặp lại theo thứ.
     */
    @Query("""
            SELECT a FROM DailyActivity a
            WHERE a.user.id = :userId
              AND a.date IS NULL
              AND (a.dayOfWeek IS NULL OR a.dayOfWeek = :dayOfWeek)
            ORDER BY a.startTime, a.sortOrder
            """)
    List<DailyActivity> findByUserIdAndDayOfWeekAndDateIsNull(
            @Param("userId") Long userId,
            @Param("dayOfWeek") Integer dayOfWeek);

    /**
     * Lấy toàn bộ lịch sinh hoạt của user.
     */
    @Query("""
            SELECT a FROM DailyActivity a
            WHERE a.user.id = :userId
            ORDER BY COALESCE(a.dayOfWeek, 0), a.startTime
            """)
    List<DailyActivity> findAllByUserId(@Param("userId") Long userId);

    /**
     * Xóa toàn bộ hoạt động của user — gọi trước khi sync sheet mới.
     */
    void deleteAllByUser(User user);
}
