package com.studybot.vocabulary;

import com.studybot.user.User;
import com.studybot.user.UserRepository;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.time.LocalDateTime;
import java.util.List;
import java.util.Optional;

@Service
@RequiredArgsConstructor
@Slf4j
public class VocabularyService {

    private final WordRepository wordRepository;
    private final UserRepository userRepository;

    // Spaced repetition intervals (giờ) theo level
    private static final int[] REVIEW_INTERVALS = {1, 4, 24, 72, 168, 336, 720};

    // ─────────────────────────────────────────────────────────────
    //  Lấy từ tiếp theo cần ôn
    // ─────────────────────────────────────────────────────────────
    public Optional<Word> getNextQuizWord(Long telegramId) {
        User user = getUser(telegramId);
        return wordRepository.findNextForReview(user, LocalDateTime.now());
    }

    // ─────────────────────────────────────────────────────────────
    //  Lấy tất cả từ vựng
    // ─────────────────────────────────────────────────────────────
    public List<Word> getAllWords(Long telegramId) {
        User user = getUser(telegramId);
        return wordRepository.findByUserOrderByCreatedAtDesc(user);
    }

    // ─────────────────────────────────────────────────────────────
    //  Thêm từ mới
    // ─────────────────────────────────────────────────────────────
    @Transactional
    public Word addWord(Long telegramId, String word, String meaning, String example) {
        User user = getUser(telegramId);

        if (word == null || word.isBlank())
            throw new IllegalArgumentException("Từ tiếng Anh không được để trống.");
        if (meaning == null || meaning.isBlank())
            throw new IllegalArgumentException("Nghĩa không được để trống.");

        Word w = Word.builder()
                .user(user)
                .word(word.trim())
                .meaning(meaning.trim())
                .example(example != null && !example.isBlank() ? example.trim() : null)
                .level(0)
                .build();

        w = wordRepository.save(w);
        log.info("✅ User {} thêm từ: '{}'", telegramId, word);
        return w;
    }

    // ─────────────────────────────────────────────────────────────
    //  Cập nhật kết quả quiz (spaced repetition)
    // ─────────────────────────────────────────────────────────────
    @Transactional
    public Word submitReview(Long telegramId, Long wordId, boolean correct) {
        User user = getUser(telegramId);
        Word w = wordRepository.findById(wordId)
                .orElseThrow(() -> new IllegalArgumentException("Không tìm thấy từ: " + wordId));

        if (!w.getUser().getId().equals(user.getId()))
            throw new IllegalArgumentException("Bạn không có quyền cập nhật từ này.");

        if (correct) {
            // Tăng level, lên tối đa 6
            int newLevel = Math.min(w.getLevel() + 1, REVIEW_INTERVALS.length - 1);
            w.setLevel(newLevel);
            int hours = REVIEW_INTERVALS[newLevel];
            w.setNextReviewAt(LocalDateTime.now().plusHours(hours));
            log.info("✅ Quiz đúng: '{}' level {} → ôn lại sau {} giờ", w.getWord(), newLevel, hours);
        } else {
            // Sai → về level 0, ôn lại ngay sau 1 giờ
            w.setLevel(0);
            w.setNextReviewAt(LocalDateTime.now().plusHours(1));
            log.info("❌ Quiz sai: '{}' → reset level 0", w.getWord());
        }

        return wordRepository.save(w);
    }

    // ─────────────────────────────────────────────────────────────
    //  Private helper
    // ─────────────────────────────────────────────────────────────
    private User getUser(Long telegramId) {
        return userRepository.findByTelegramId(telegramId)
                .orElseThrow(() -> new RuntimeException(
                        "User chưa đăng ký. Vui lòng dùng /start trước."));
    }
}
