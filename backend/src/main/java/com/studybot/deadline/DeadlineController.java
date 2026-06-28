package com.studybot.deadline;

import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;
import java.util.Map;

/**
 * REST Controller cho Deadline API.
 *
 * GET  /api/deadlines/{telegramId}          — lấy danh sách chưa xong
 * POST /api/deadlines                        — thêm mới
 * PATCH /api/deadlines/{id}/done?telegramId  — đánh dấu đã xong
 */
@RestController
@RequestMapping("/deadlines")
@RequiredArgsConstructor
public class DeadlineController {

    private final DeadlineService deadlineService;

    // ─────────────────────────────────────────────────────────────
    //  1. Lấy danh sách deadline chưa hoàn thành
    //  GET /api/deadlines/{telegramId}
    // ─────────────────────────────────────────────────────────────
    @GetMapping("/{telegramId}")
    public ResponseEntity<List<Map<String, Object>>> getDeadlines(
            @PathVariable Long telegramId) {

        List<Deadline> deadlines = deadlineService.getPendingDeadlines(telegramId);
        List<Map<String, Object>> result = deadlines.stream()
                .map(this::toMap)
                .toList();
        return ResponseEntity.ok(result);
    }

    // ─────────────────────────────────────────────────────────────
    //  2. Thêm deadline mới
    //  POST /api/deadlines
    //  Body: { telegramId, title, dueDate, subject? }
    // ─────────────────────────────────────────────────────────────
    @PostMapping
    public ResponseEntity<Map<String, Object>> addDeadline(
            @RequestBody Map<String, Object> body) {

        Long   telegramId = getLong(body, "telegramId");
        String title      = getString(body, "title");
        String dueDate    = getString(body, "dueDate");
        String subject    = (String) body.getOrDefault("subject", null);

        if (title == null || title.isBlank())
            throw new IllegalArgumentException("Tiêu đề deadline không được để trống.");
        if (dueDate == null || dueDate.isBlank())
            throw new IllegalArgumentException("Ngày hạn không được để trống (YYYY-MM-DD).");

        Deadline dl = deadlineService.addDeadline(telegramId, title, dueDate, subject);
        return ResponseEntity.status(201).body(Map.of(
                "id",      dl.getId(),
                "title",   dl.getTitle(),
                "dueDate", dl.getDueDate().toString(),
                "subject", dl.getSubject() != null ? dl.getSubject() : "",
                "isDone",  dl.getIsDone(),
                "message", "✅ Đã thêm deadline: " + dl.getTitle()
        ));
    }

    // ─────────────────────────────────────────────────────────────
    //  3. Đánh dấu hoàn thành
    //  PATCH /api/deadlines/{id}/done?telegramId=xxx
    // ─────────────────────────────────────────────────────────────
    @PatchMapping("/{id}/done")
    public ResponseEntity<Map<String, Object>> markDone(
            @PathVariable Long id,
            @RequestParam Long telegramId) {

        Deadline dl = deadlineService.markDone(telegramId, id);
        return ResponseEntity.ok(Map.of(
                "id",      dl.getId(),
                "title",   dl.getTitle(),
                "isDone",  dl.getIsDone(),
                "message", "✅ Đã đánh dấu xong: " + dl.getTitle()
        ));
    }

    // ─────────────────────────────────────────────────────────────
    //  Helpers
    // ─────────────────────────────────────────────────────────────
    private Map<String, Object> toMap(Deadline dl) {
        return Map.of(
                "id",      dl.getId(),
                "title",   dl.getTitle(),
                "dueDate", dl.getDueDate().toString(),
                "subject", dl.getSubject() != null ? dl.getSubject() : "",
                "isDone",  dl.getIsDone(),
                "note",    dl.getNote()   != null ? dl.getNote()    : ""
        );
    }

    private Long getLong(Map<String, Object> body, String key) {
        Object v = body.get(key);
        if (v == null) throw new IllegalArgumentException("Thiếu field: " + key);
        return ((Number) v).longValue();
    }

    private String getString(Map<String, Object> body, String key) {
        Object v = body.get(key);
        return v != null ? v.toString() : null;
    }
}
