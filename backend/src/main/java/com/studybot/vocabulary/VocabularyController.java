package com.studybot.vocabulary;

import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;
import java.util.Map;
import java.util.Optional;

/**
 * REST Controller cho Vocabulary API.
 *
 * GET  /api/vocabulary/{telegramId}        — lấy tất cả từ
 * GET  /api/vocabulary/{telegramId}/next   — từ tiếp theo cần ôn (204 nếu không có)
 * POST /api/vocabulary                     — thêm từ mới
 * POST /api/vocabulary/{wordId}/review     — nộp kết quả quiz
 */
@RestController
@RequestMapping("/vocabulary")
@RequiredArgsConstructor
public class VocabularyController {

    private final VocabularyService vocabularyService;

    // ─────────────────────────────────────────────────────────────
    //  1. Lấy từ tiếp theo cần ôn
    //  GET /api/vocabulary/{telegramId}/next
    // ─────────────────────────────────────────────────────────────
    @GetMapping("/{telegramId}/next")
    public ResponseEntity<?> getNextQuizWord(@PathVariable Long telegramId) {
        Optional<Word> word = vocabularyService.getNextQuizWord(telegramId);
        if (word.isEmpty()) {
            return ResponseEntity.noContent().build();   // 204 — bot xử lý riêng
        }
        return ResponseEntity.ok(toMap(word.get()));
    }

    // ─────────────────────────────────────────────────────────────
    //  2. Lấy tất cả từ vựng
    //  GET /api/vocabulary/{telegramId}
    // ─────────────────────────────────────────────────────────────
    @GetMapping("/{telegramId}")
    public ResponseEntity<List<Map<String, Object>>> getAllWords(@PathVariable Long telegramId) {
        List<Word> words = vocabularyService.getAllWords(telegramId);
        return ResponseEntity.ok(words.stream().map(this::toMap).toList());
    }

    // ─────────────────────────────────────────────────────────────
    //  3. Thêm từ mới
    //  POST /api/vocabulary
    //  Body: { telegramId, word, meaning, example? }
    // ─────────────────────────────────────────────────────────────
    @PostMapping
    public ResponseEntity<Map<String, Object>> addWord(
            @RequestBody Map<String, Object> body) {

        Long   telegramId = getLong(body, "telegramId");
        String word       = getString(body, "word");
        String meaning    = getString(body, "meaning");
        String example    = (String) body.getOrDefault("example", null);

        Word w = vocabularyService.addWord(telegramId, word, meaning, example);
        return ResponseEntity.status(201).body(Map.of(
                "id",      w.getId(),
                "word",    w.getWord(),
                "meaning", w.getMeaning(),
                "level",   w.getLevel(),
                "message", "✅ Đã thêm từ: " + w.getWord()
        ));
    }

    // ─────────────────────────────────────────────────────────────
    //  4. Nộp kết quả quiz (spaced repetition)
    //  POST /api/vocabulary/{wordId}/review
    //  Body: { telegramId, correct }
    // ─────────────────────────────────────────────────────────────
    @PostMapping("/{wordId}/review")
    public ResponseEntity<Map<String, Object>> submitReview(
            @PathVariable Long wordId,
            @RequestBody Map<String, Object> body) {

        Long    telegramId = getLong(body, "telegramId");
        boolean correct    = Boolean.TRUE.equals(body.get("correct"));

        Word w = vocabularyService.submitReview(telegramId, wordId, correct);
        return ResponseEntity.ok(Map.of(
                "id",            w.getId(),
                "word",          w.getWord(),
                "level",         w.getLevel(),
                "nextReviewAt",  w.getNextReviewAt().toString(),
                "message",       correct ? "✅ Đúng! Level " + w.getLevel()
                                         : "❌ Sai. Ôn lại sau 1 giờ"
        ));
    }

    // ─────────────────────────────────────────────────────────────
    //  Helpers
    // ─────────────────────────────────────────────────────────────
    private Map<String, Object> toMap(Word w) {
        return Map.of(
                "id",            w.getId(),
                "word",          w.getWord(),
                "meaning",       w.getMeaning(),
                "pronunciation", w.getPronunciation() != null ? w.getPronunciation() : "",
                "example",       w.getExample()       != null ? w.getExample()       : "",
                "level",         w.getLevel(),
                "nextReviewAt",  w.getNextReviewAt()  != null ? w.getNextReviewAt().toString() : ""
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
