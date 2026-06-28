package com.studybot.exam;

import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;
import java.util.Map;

/**
 * REST Controller cho Exam (Lịch thi) API.
 *
 * GET  /api/exams/{telegramId}  — lấy danh sách lịch thi
 * POST /api/exams               — thêm lịch thi mới
 */
@RestController
@RequestMapping("/exams")
@RequiredArgsConstructor
public class ExamController {

    private final ExamService examService;

    // ─────────────────────────────────────────────────────────────
    //  1. Lấy danh sách lịch thi
    //  GET /api/exams/{telegramId}
    // ─────────────────────────────────────────────────────────────
    @GetMapping("/{telegramId}")
    public ResponseEntity<List<Map<String, Object>>> getExams(
            @PathVariable Long telegramId) {

        List<Exam> exams = examService.getExams(telegramId);
        List<Map<String, Object>> result = exams.stream()
                .map(this::toMap)
                .toList();
        return ResponseEntity.ok(result);
    }

    // ─────────────────────────────────────────────────────────────
    //  2. Thêm lịch thi mới
    //  POST /api/exams
    //  Body: { telegramId, subject, examDate, startTime, room?, examType? }
    // ─────────────────────────────────────────────────────────────
    @PostMapping
    public ResponseEntity<Map<String, Object>> addExam(
            @RequestBody Map<String, Object> body) {

        Long   telegramId = getLong(body, "telegramId");
        String subject    = getString(body, "subject");
        String examDate   = getString(body, "examDate");
        String startTime  = getString(body, "startTime");
        String room       = (String) body.getOrDefault("room", null);
        String examType   = (String) body.getOrDefault("examType", null);

        if (subject == null || subject.isBlank())
            throw new IllegalArgumentException("Tên môn thi không được để trống.");
        if (examDate == null || examDate.isBlank())
            throw new IllegalArgumentException("Ngày thi không được để trống (YYYY-MM-DD).");
        if (startTime == null || startTime.isBlank())
            throw new IllegalArgumentException("Giờ thi không được để trống (HH:MM).");

        Exam exam = examService.addExam(telegramId, subject, examDate,
                                        startTime, room, examType);
        return ResponseEntity.status(201).body(Map.of(
                "id",        exam.getId(),
                "subject",   exam.getSubject(),
                "examDate",  exam.getExamDate().toString(),
                "startTime", exam.getStartTime().toString(),
                "room",      exam.getRoom()     != null ? exam.getRoom()     : "",
                "examType",  exam.getExamType() != null ? exam.getExamType() : "",
                "message",   "✅ Đã thêm lịch thi: " + exam.getSubject()
        ));
    }

    // ─────────────────────────────────────────────────────────────
    //  Helpers
    // ─────────────────────────────────────────────────────────────
    private Map<String, Object> toMap(Exam e) {
        return Map.of(
                "id",        e.getId(),
                "subject",   e.getSubject(),
                "examDate",  e.getExamDate().toString(),
                "startTime", e.getStartTime().toString(),
                "room",      e.getRoom()     != null ? e.getRoom()     : "",
                "examType",  e.getExamType() != null ? e.getExamType() : ""
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
