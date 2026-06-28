package com.studybot.user;

import lombok.Getter;
import lombok.Setter;

/**
 * Request body để cập nhật notification settings.
 * Tất cả fields đều Optional — chỉ field nào được gửi mới được update.
 */
@Getter
@Setter
public class NotificationSettingsRequest {
    private Long telegramId;           // bắt buộc

    // Bật/tắt từng loại
    private Boolean notifyDailySummary;   // Tóm tắt sáng mỗi ngày
    private Boolean notifyClassRemind;    // Nhắc trước buổi học
    private Boolean notifyDeadline;       // Nhắc deadline sắp hết hạn
    private Boolean notifyExam;           // Nhắc lịch thi sắp tới
    private Boolean notifyHustEvents;     // tự động sync sự kiện HUST

    // Cấu hình thời gian
    private String  dailySummaryTime;     // "HH:mm" — giờ gửi tóm tắt sáng
    private Short   classRemindBefore;    // phút trước buổi học
    private Short   deadlineRemindBefore; // phút trước deadline (1440 = 1 ngày)
    private Short   examRemindBeforeDays; // ngày trước lịch thi
}
