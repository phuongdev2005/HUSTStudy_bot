package com.studybot.schedule;

import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;

import java.time.LocalDate;
import java.util.List;

/**
 * Repository cho bảng "class_schedules".
 */
@Repository
public interface ClassScheduleRepository extends JpaRepository<ClassSession, Long> {

    /**
     * Lấy lịch học theo ngày cụ thể.
     */
    @Query("""
            SELECT cs FROM ClassSession cs
            JOIN FETCH cs.subject s
            WHERE s.user.id = :userId
              AND cs.date = :date
              AND s.isActive = true
            ORDER BY cs.startTime
            """)
    List<ClassSession> findByUserIdAndDate(
            @Param("userId") Long userId,
            @Param("date") LocalDate date);

    /**
     * Lấy lịch học hàng tuần lặp lại theo thứ.
     */
    @Query("""
            SELECT cs FROM ClassSession cs
            JOIN FETCH cs.subject s
            WHERE s.user.id = :userId
              AND cs.date IS NULL
              AND cs.dayOfWeek = :dayOfWeek
              AND s.isActive = true
            ORDER BY cs.startTime
            """)
    List<ClassSession> findByUserIdAndDayOfWeekAndDateIsNull(
            @Param("userId") Long userId,
            @Param("dayOfWeek") Integer dayOfWeek);
}
