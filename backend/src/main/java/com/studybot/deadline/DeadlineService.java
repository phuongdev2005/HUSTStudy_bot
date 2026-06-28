package com.studybot.deadline;

import com.studybot.user.User;
import com.studybot.user.UserRepository;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.time.LocalDate;
import java.util.List;

@Service
@RequiredArgsConstructor
@Slf4j
public class DeadlineService {

    private final DeadlineRepository deadlineRepository;
    private final UserRepository     userRepository;

    // ─────────────────────────────────────────────────────────────
    //  Lấy danh sách deadline chưa hoàn thành
    // ─────────────────────────────────────────────────────────────
    public List<Deadline> getPendingDeadlines(Long telegramId) {
        User user = getUser(telegramId);
        return deadlineRepository.findPendingByUser(user, LocalDate.now());
    }

    // ─────────────────────────────────────────────────────────────
    //  Thêm deadline mới
    // ─────────────────────────────────────────────────────────────
    @Transactional
    public Deadline addDeadline(Long telegramId, String title,
                                String dueDateStr, String subject) {
        User user = getUser(telegramId);

        LocalDate dueDate;
        try {
            dueDate = LocalDate.parse(dueDateStr);   // ISO format: yyyy-MM-dd
        } catch (Exception e) {
            throw new IllegalArgumentException(
                "Ngày không hợp lệ: '" + dueDateStr + "'. Dùng định dạng YYYY-MM-DD");
        }

        Deadline dl = Deadline.builder()
                .user(user)
                .title(title.trim())
                .subject(subject != null && !subject.isBlank() ? subject.trim() : null)
                .dueDate(dueDate)
                .isDone(false)
                .build();

        dl = deadlineRepository.save(dl);
        log.info("✅ User {} thêm deadline: '{}' hạn {}", telegramId, title, dueDate);
        return dl;
    }

    // ─────────────────────────────────────────────────────────────
    //  Đánh dấu đã xong
    // ─────────────────────────────────────────────────────────────
    @Transactional
    public Deadline markDone(Long telegramId, Long deadlineId) {
        User user = getUser(telegramId);
        Deadline dl = deadlineRepository.findById(deadlineId)
                .orElseThrow(() -> new IllegalArgumentException("Không tìm thấy deadline: " + deadlineId));

        if (!dl.getUser().getId().equals(user.getId())) {
            throw new IllegalArgumentException("Bạn không có quyền sửa deadline này.");
        }

        dl.setIsDone(true);
        dl = deadlineRepository.save(dl);
        log.info("✅ User {} đánh dấu xong deadline #{}: '{}'", telegramId, deadlineId, dl.getTitle());
        return dl;
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
