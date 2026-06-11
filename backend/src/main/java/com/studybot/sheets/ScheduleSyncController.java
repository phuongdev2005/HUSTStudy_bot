package com.studybot.sheets;

import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;
import java.util.Map;

/**
 * REST Controller cho tính năng Google Sheet Schedule.
 *
 * Base URL: /api/schedule
 *
 * Endpoints:
 *   POST /api/schedule/{telegramId}/setsheet   → lưu link sheet
 *   POST /api/schedule/{telegramId}/sync        → trigger sync từ sheet
 *   GET  /api/schedule/{telegramId}/today       → lịch học hôm nay
 *   GET  /api/schedule/{telegramId}/week        → lịch học cả tuần
 */
@RestController
@RequestMapping("/schedule")
@RequiredArgsConstructor
public class ScheduleSyncController {

    private final SheetsService sheetsService;

    /**
     * Lưu link Google Sheet của user.
     *
     * POST /api/schedule/{telegramId}/setsheet
     * Body: { "sheetUrl": "https://docs.google.com/spreadsheets/d/..." }
     *
     * Response: 200 OK → { "message": "✅ Đã lưu Google Sheet..." }
     */
    @PostMapping("/{telegramId}/setsheet")
    public ResponseEntity<Map<String, String>> setSheet(
            @PathVariable Long telegramId,
            @RequestBody Map<String, String> body) {

        String sheetUrl = body.get("sheetUrl");
        if (sheetUrl == null || sheetUrl.isBlank()) {
            return ResponseEntity.badRequest()
                    .body(Map.of("message", "❌ sheetUrl không được để trống"));
        }

        String result = sheetsService.setSheetUrl(telegramId, sheetUrl);
        return ResponseEntity.ok(Map.of("message", result));
    }

    /**
     * Trigger sync dữ liệu từ Google Sheet vào DB.
     *
     * POST /api/schedule/{telegramId}/sync
     *
     * Response 200 OK:
     * {
     *   "success":     true,
     *   "syncedCount": 12,
     *   "errors":      [],
     *   "message":     "✅ Đồng bộ thành công 12 buổi học!"
     * }
     */
    @PostMapping("/{telegramId}/sync")
    public ResponseEntity<SyncResult> syncSheet(@PathVariable Long telegramId) {
        SyncResult result = sheetsService.syncScheduleFromSheet(telegramId);
        // Luôn trả 200 – success/failure nằm trong body để bot xử lý
        return ResponseEntity.ok(result);
    }

    /**
     * Lấy lịch học hôm nay của user.
     *
     * GET /api/schedule/{telegramId}/today
     *
     * Response: 200 OK → [ { "subjectName": "...", "startTime": "...", ... }, ... ]
     */
    @GetMapping("/{telegramId}/today")
    public ResponseEntity<List<ScheduleItem>> getToday(@PathVariable Long telegramId) {
        List<ScheduleItem> schedule = sheetsService.getTodaySchedule(telegramId);
        return ResponseEntity.ok(schedule);
    }

    /**
     * Lấy toàn bộ lịch học trong tuần của user.
     *
     * GET /api/schedule/{telegramId}/week
     */
    @GetMapping("/{telegramId}/week")
    public ResponseEntity<List<ScheduleItem>> getWeek(@PathVariable Long telegramId) {
        List<ScheduleItem> schedule = sheetsService.getWeeklySchedule(telegramId);
        return ResponseEntity.ok(schedule);
    }
}
