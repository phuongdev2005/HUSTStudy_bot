package com.studybot.schedule;

import jakarta.persistence.*;
import lombok.*;

/**
 * Entity buổi học (tiết học cụ thể trong tuần).
 * Một môn học có thể có nhiều buổi: Thứ 2 tiết 1-3, Thứ 5 tiết 7-9, ...
 */
@Entity
@Table(name = "class_sessions")
@Getter @Setter
@NoArgsConstructor @AllArgsConstructor
@Builder
public class ClassSession {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "subject_id", nullable = false)
    private Subject subject;

    /**
     * Thứ trong tuần: 2 = Thứ 2, 3 = Thứ 3, ... 8 = Chủ nhật
     */
    @Column(name = "day_of_week", nullable = false)
    private Integer dayOfWeek;

    @Column(name = "start_time", nullable = false, length = 5)
    private String startTime;         // HH:mm (vd: "07:00")

    @Column(name = "end_time", nullable = false, length = 5)
    private String endTime;           // HH:mm (vd: "09:30")

    @Column(name = "room", length = 50)
    private String room;              // Phòng học (vd: "B1-301")

    /**
     * Tuần chẵn / lẻ / tất cả.
     * Giá trị: "ALL", "EVEN", "ODD"
     */
    @Builder.Default
    @Column(name = "week_type", length = 10)
    private String weekType = "ALL";
}
