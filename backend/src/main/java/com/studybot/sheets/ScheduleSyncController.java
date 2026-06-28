package com.studybot.sheets;

import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.time.DayOfWeek;
import java.time.LocalDate;
import java.util.List;
import java.util.Map;

/**
 * REST Controller cho tính năng Google Sheet Schedule.
 *
 * Base URL: /api/schedule
 *
 * Endpoints:
 *   POST /api/schedule/{telegramId}/setsheet    → lưu link sheet
 *   POST /api/schedule/{telegramId}/sync         → sync lịch học (format 7 cột cũ)
 *   POST /api/schedule/{telegramId}/sync-daily   → sync lịch sinh hoạt (format 6 cột mới)
 *   GET  /api/schedule/{telegramId}/today        → lịch học hôm nay
 *   GET  /api/schedule/{telegramId}/week         → lịch học cả tuần
 *   GET  /api/schedule/{telegramId}/daily        → lịch sinh hoạt hôm nay (full timeline)
 *   GET  /api/schedule/{telegramId}/daily/all    → lịch sinh hoạt toàn bộ
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
     * Trigger sync lịch sinh hoạt — TỰ ĐỘNG nhận dạng format:
     *   - Grid format (hàng=giờ, cột=ngày): header có "Thứ 2, Thứ 3..."
     *   - Row format (6 cột): header có "Thứ | Giờ bắt | Giờ kết | ..."
     *
     * POST /api/schedule/{telegramId}/sync-daily
     */
    @PostMapping("/{telegramId}/sync-daily")
    public ResponseEntity<SyncResult> syncDailySheet(@PathVariable Long telegramId) {
        SyncResult result = sheetsService.autoSyncSheet(telegramId);
        return ResponseEntity.ok(result);
    }

    /**
     * Lấy lịch sinh hoạt hôm nay (kết hợp hoạt động mọi ngày + ngày đó).
     *
     * GET /api/schedule/{telegramId}/daily
     * Optional param: ?day=2 (mặc định = hôm nay)
     */
    @GetMapping("/{telegramId}/daily")
    public ResponseEntity<List<DailyActivityItem>> getDaily(
            @PathVariable Long telegramId,
            @RequestParam(required = false) Integer day) {

        LocalDate targetDate;
        if (day != null) {
            targetDate = LocalDate.now().with(java.time.DayOfWeek.of(day));
        } else {
            targetDate = LocalDate.now();
        }

        List<DailyActivityItem> items = sheetsService.getDailyActivities(telegramId, targetDate);
        return ResponseEntity.ok(items);
    }

    /**
     * Lấy toàn bộ lịch sinh hoạt của user (mọi ngày).
     *
     * GET /api/schedule/{telegramId}/daily/all
     */
    @GetMapping("/{telegramId}/daily/all")
    public ResponseEntity<List<DailyActivityItem>> getAllDaily(@PathVariable Long telegramId) {
        return ResponseEntity.ok(sheetsService.getAllDailyActivities(telegramId));
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
