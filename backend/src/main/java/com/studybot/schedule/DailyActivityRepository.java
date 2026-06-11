package com.studybot.schedule;

import com.studybot.user.User;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;

import java.util.List;

/**
 * Repository cho bảng "daily_activities".
 */
@Repository
public interface DailyActivityRepository extends JpaRepository<DailyActivity, Long> {

    /**
     * Lấy lịch của 1 ngày cụ thể:
     *   - Hoạt động mọi ngày (day_of_week IS NULL)  ← ăn, ngủ, vệ sinh
     *   - Hoạt động riêng ngày đó (day_of_week = ?) ← lịch học hôm nay
     * Sắp xếp theo giờ bắt đầu.
     */
    @Query("""
            SELECT a FROM DailyActivity a
            WHERE a.user.id = :userId
              AND (a.dayOfWeek IS NULL OR a.dayOfWeek = :dayOfWeek)
            ORDER BY a.startTime, a.sortOrder
            """)
    List<DailyActivity> findDayActivities(
            @Param("userId") Long userId,
            @Param("dayOfWeek") Integer dayOfWeek);

    /**
     * Lấy toàn bộ lịch của user (tất cả các ngày).
     * Dùng cho /timetable — xem lịch cả tuần.
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
