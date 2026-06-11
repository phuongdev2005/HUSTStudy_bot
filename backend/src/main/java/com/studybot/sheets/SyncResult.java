package com.studybot.sheets;

import lombok.Getter;

import java.util.List;

/**
 * DTO kết quả của lệnh sync Google Sheet.
 * Trả về JSON cho Python Bot.
 */
@Getter
public class SyncResult {

    private final boolean success;
    private final int syncedCount;          // Số buổi học đã sync thành công
    private final List<String> errors;      // Danh sách lỗi theo từng hàng
    private final String message;           // Thông báo tổng quát

    private SyncResult(boolean success, int syncedCount, List<String> errors, String message) {
        this.success     = success;
        this.syncedCount = syncedCount;
        this.errors      = errors;
        this.message     = message;
    }

    public static SyncResult success(int count, List<String> errors) {
        String msg;
        if (errors.isEmpty()) {
            msg = "✅ Đồng bộ thành công " + count + " buổi học!";
        } else {
            msg = "⚠️ Đồng bộ " + count + " buổi học, bỏ qua " + errors.size() + " dòng lỗi.";
        }
        return new SyncResult(true, count, errors, msg);
    }

    public static SyncResult error(String message) {
        return new SyncResult(false, 0, List.of(), message);
    }
}
