package com.studybot.user;

import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

/**
 * Service xử lý nghiệp vụ liên quan đến User.
 *
 * Luồng: Controller → Service → Repository → DB
 */
@Service
@RequiredArgsConstructor
public class UserService {

    private final UserRepository userRepository;

    /**
     * Đăng ký user mới hoặc cập nhật nếu đã tồn tại.
     * Gọi khi user dùng lệnh /start trên Telegram.
     *
     * Logic:
     *   - Nếu user đã có → cập nhật tên/username
     *   - Nếu chưa có   → tạo mới + tạo UserSettings mặc định
     */
    @Transactional
    public UserResponse registerOrUpdate(UserRequest request) {
        User user = userRepository.findByTelegramId(request.getTelegramId())
                .orElse(null);

        if (user == null) {
            user = createNewUser(request);
        } else {
            user.setFullName(request.getFullName());
            user.setUsername(request.getUsername());
            user.setIsActive(true);
        }

        user = userRepository.save(user);
        return UserResponse.from(user);
    }

    /**
     * Lấy thông tin user theo Telegram ID.
     */
    @Transactional(readOnly = true)
    public UserResponse getByTelegramId(Long telegramId) {
        User user = userRepository.findByTelegramId(telegramId)
                .orElseThrow(() ->
                    new RuntimeException("Không tìm thấy user với telegramId: " + telegramId)
                );
        return UserResponse.from(user);
    }

    /**
     * Kiểm tra user đã đăng ký chưa.
     */
    @Transactional(readOnly = true)
    public boolean existsByTelegramId(Long telegramId) {
        return userRepository.existsByTelegramId(telegramId);
    }

    // ── Private helpers ────────────────────────────────────────────

    private User createNewUser(UserRequest request) {
        User newUser = User.builder()
                .telegramId(request.getTelegramId())
                .username(request.getUsername())
                .fullName(request.getFullName())
                .languageCode(request.getLanguageCode())
                .timezone(request.getTimezone())
                .isActive(true)
                .build();

        UserSettings settings = UserSettings.builder()
                .user(newUser)
                .notifyClassRemind(true)
                .notifyDeadline(true)
                .notifyExam(true)
                .notifyBudgetWarn(true)
                .notifyDailySummary(true)
                .classRemindBefore((short) 30)
                .deadlineRemindBefore((short) 1440)
                .examRemindBeforeDays((short) 2)
                .build();

        newUser.setSettings(settings);
        return newUser;
    }
}
