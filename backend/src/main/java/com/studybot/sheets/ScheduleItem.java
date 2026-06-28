package com.studybot.sheets;

import com.studybot.schedule.ClassSession;
import lombok.Getter;

/**
 * DTO một buổi học — trả về cho Python Bot để hiển thị.
 *
 * JSON example:
 * {
 *   "subjectName": "Giải tích 1",
 *   "subjectCode": "MA1010",
 *   "dayOfWeek": 2,
 *   "startTime": "07:00",
 *   "endTime":   "09:30",
 *   "room":      "B1-301",
 *   "teacher":   "Nguyễn A"
 * }
 */
@Getter
public class ScheduleItem {

    private final Long sessionId;
    private final String subjectName;
    private final String subjectCode;
    private final Integer dayOfWeek;      // 1=T2 … 7=CN
    private final String startTime;       // HH:mm
    private final String endTime;         // HH:mm
    private final String room;
    private final String teacher;
    private final String date;            // yyyy-MM-dd (null if recurring)

    private ScheduleItem(Long sessionId, String subjectName, String subjectCode,
                         Integer dayOfWeek, String startTime, String endTime,
                         String room, String teacher, String date) {
        this.sessionId   = sessionId;
        this.subjectName = subjectName;
        this.subjectCode = subjectCode;
        this.dayOfWeek   = dayOfWeek;
        this.startTime   = startTime;
        this.endTime     = endTime;
        this.room        = room;
        this.teacher     = teacher;
        this.date        = date;
    }

    /** Factory từ ClassSession entity. */
    public static ScheduleItem from(ClassSession cs) {
        return new ScheduleItem(
                cs.getId(),
                cs.getSubject().getName(),
                cs.getSubject().getCode(),
                cs.getDayOfWeek(),
                cs.getStartTime(),
                cs.getEndTime(),
                cs.getRoom(),
                cs.getSubject().getTeacher(),
                cs.getDate() != null ? cs.getDate().toString() : null
        );
    }
}
