package com.studybot.user;

import lombok.Getter;

/**
 * Response trả về trạng thái notification settings hiện tại.
 */
@Getter
public class NotificationSettingsResponse {

    private final boolean notifyDailySummary;
    private final boolean notifyClassRemind;
    private final boolean notifyDeadline;
    private final boolean notifyExam;
    private final boolean notifyHustEvents;

    private final String dailySummaryTime;     // "HH:mm"
    private final int    classRemindBefore;    // phút
    private final int    deadlineRemindBefore; // phút
    private final int    examRemindBeforeDays; // ngày

    private NotificationSettingsResponse(UserSettings s) {
        this.notifyDailySummary   = Boolean.TRUE.equals(s.getNotifyDailySummary());
        this.notifyClassRemind    = Boolean.TRUE.equals(s.getNotifyClassRemind());
        this.notifyDeadline       = Boolean.TRUE.equals(s.getNotifyDeadline());
        this.notifyExam           = Boolean.TRUE.equals(s.getNotifyExam());
        this.notifyHustEvents     = Boolean.TRUE.equals(s.getNotifyHustEvents());
        this.dailySummaryTime     = s.getDailySummaryTime() != null
                                    ? s.getDailySummaryTime().toString().substring(0, 5)
                                    : "07:00";
        this.classRemindBefore    = s.getClassRemindBefore()    != null ? s.getClassRemindBefore()    : 30;
        this.deadlineRemindBefore = s.getDeadlineRemindBefore() != null ? s.getDeadlineRemindBefore() : 1440;
        this.examRemindBeforeDays = s.getExamRemindBeforeDays() != null ? s.getExamRemindBeforeDays() : 2;
    }

    public static NotificationSettingsResponse from(UserSettings s) {
        return new NotificationSettingsResponse(s);
    }
}
