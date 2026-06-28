package com.studybot.sheets;

import com.studybot.schedule.DailyActivity;
import lombok.Getter;

/**
 * DTO 1 khung giờ hoạt động — trả về cho Python Bot.
 *
 * JSON example:
 * {
 *   "startTime": "06:30",
 *   "endTime":   "07:00",
 *   "activity":  "Vệ sinh cá nhân",
 *   "category":  "Sinh hoạt",
 *   "note":      null,
 *   "dayOfWeek": null
 * }
 */
@Getter
public class DailyActivityItem {

    private final Long id;
    private final Integer dayOfWeek;   // null = mọi ngày; 1=T2..7=CN
    private final String startTime;    // HH:mm
    private final String endTime;      // HH:mm
    private final String activity;     // Tên hoạt động
    private final String category;     // Danh mục
    private final String note;         // Ghi chú
    private final String date;         // yyyy-MM-dd (null if recurring)

    private DailyActivityItem(Long id, Integer dayOfWeek, String startTime, String endTime,
                               String activity, String category, String note, String date) {
        this.id         = id;
        this.dayOfWeek  = dayOfWeek;
        this.startTime  = startTime;
        this.endTime    = endTime;
        this.activity   = activity;
        this.category   = category;
        this.note       = note;
        this.date       = date;
    }

    /** Factory từ DailyActivity entity. */
    public static DailyActivityItem from(DailyActivity a) {
        return new DailyActivityItem(
                a.getId(),
                a.getDayOfWeek(),
                a.getStartTime(),
                a.getEndTime(),
                a.getActivity(),
                a.getCategory(),
                a.getNote(),
                a.getDate() != null ? a.getDate().toString() : null
        );
    }
}
