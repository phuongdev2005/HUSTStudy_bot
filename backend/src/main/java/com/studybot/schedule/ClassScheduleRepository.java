package com.studybot.schedule;

import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;

import java.util.List;

/**
 * Repository cho bảng "class_schedules".
 */
@Repository
public interface ClassScheduleRepository extends JpaRepository<ClassSession, Long> {

    /**
     * Lấy lịch học hôm nay của user theo dayOfWeek.
     * dayOfWeek: 1=T2, 2=T3, 3=T4, 4=T5, 5=T6, 6=T7, 7=CN
     */
    @Query("""
            SELECT cs FROM ClassSession cs
            JOIN FETCH cs.subject s
            WHERE s.user.id = :userId
              AND cs.dayOfWeek = :dayOfWeek
              AND s.isActive = true
            ORDER BY cs.startTime
            """)
    List<ClassSession> findTodayByUserId(
            @Param("userId") Long userId,
            @Param("dayOfWeek") Integer dayOfWeek);

    /**
     * Lấy toàn bộ lịch học trong tuần của user.
     */
    @Query("""
            SELECT cs FROM ClassSession cs
            JOIN FETCH cs.subject s
            WHERE s.user.id = :userId
              AND s.isActive = true
            ORDER BY cs.dayOfWeek, cs.startTime
            """)
    List<ClassSession> findWeeklyByUserId(@Param("userId") Long userId);
}
