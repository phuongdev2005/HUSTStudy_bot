package com.studybot.user;

import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.List;
import java.util.Map;
import java.util.HashMap;

/**
 * Service xử lý nghiệp vụ liên quan đến User.
 *
 * Luồng: Controller → Service → Repository → DB
 */
@Service
@RequiredArgsConstructor
public class UserService {

    private final UserRepository         userRepository;
    private final UserSettingsRepository userSettingsRepository;

    /**
     * Đăng ký user mới hoặc cập nhật nếu đã tồn tại.
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
     * Kiểm tra user đã đăng ký chưa.
     */
    @Transactional(readOnly = true)
    public boolean existsByTelegramId(Long telegramId) {
        return userRepository.existsByTelegramId(telegramId);
    }

    /**
     * Lấy cài đặt thông báo của user.
     */
    @Transactional(readOnly = true)
    public NotificationSettingsResponse getNotificationSettings(Long telegramId) {
        User user = userRepository.findByTelegramId(telegramId)
                .orElseThrow(() -> new RuntimeException("User không tồn tại: " + telegramId));
        UserSettings s = userSettingsRepository.findByUser(user)
                .orElseThrow(() -> new RuntimeException("Không tìm thấy settings"));
        return NotificationSettingsResponse.from(s);
    }

    /**
     * Cập nhật cài đặt thông báo — chỉ field nào có giá trị mới được update.
     */
    @Transactional
    public NotificationSettingsResponse updateNotificationSettings(NotificationSettingsRequest req) {
        User user = userRepository.findByTelegramId(req.getTelegramId())
                .orElseThrow(() -> new RuntimeException("User không tồn tại: " + req.getTelegramId()));
        UserSettings s = userSettingsRepository.findByUser(user)
                .orElseThrow(() -> new RuntimeException("Không tìm thấy settings"));

        if (req.getNotifyDailySummary()   != null) s.setNotifyDailySummary(req.getNotifyDailySummary());
        if (req.getNotifyClassRemind()     != null) s.setNotifyClassRemind(req.getNotifyClassRemind());
        if (req.getNotifyDeadline()        != null) s.setNotifyDeadline(req.getNotifyDeadline());
        if (req.getNotifyExam()            != null) s.setNotifyExam(req.getNotifyExam());
        if (req.getNotifyHustEvents()      != null) s.setNotifyHustEvents(req.getNotifyHustEvents());
        if (req.getClassRemindBefore()     != null) s.setClassRemindBefore(req.getClassRemindBefore());
        if (req.getDeadlineRemindBefore()  != null) s.setDeadlineRemindBefore(req.getDeadlineRemindBefore());
        if (req.getExamRemindBeforeDays()  != null) s.setExamRemindBeforeDays(req.getExamRemindBeforeDays());
        if (req.getDailySummaryTime()      != null) {
            try {
                s.setDailySummaryTime(java.time.LocalTime.parse(req.getDailySummaryTime()));
            } catch (Exception ignored) {}
        }

        userSettingsRepository.save(s);
        return NotificationSettingsResponse.from(s);
    }

    // ── Private helpers ────────────────────────────────────────────

    /**
     * User block bot → set isActive = false.
     * Gọi từ Python bot khi nhận sự kiện my_chat_member với status "kicked".
     */
    @Transactional
    public void deactivate(Long telegramId) {
        userRepository.findByTelegramId(telegramId).ifPresent(user -> {
            user.setIsActive(false);
            userRepository.save(user);
        });
    }

    // ── Private helpers ────────────────────────────────────────────

    private User createNewUser(UserRequest request) {
        User newUser = User.builder()
                .telegramId(request.getTelegramId())
                .username(request.getUsername())
                .fullName(request.getFullName())
                .isActive(true)
                .build();

        UserSettings settings = UserSettings.builder()
                .user(newUser)
                .notifyClassRemind(true)
                .notifyDeadline(true)
                .notifyExam(true)
                .notifyDailySummary(true)
                .classRemindBefore((short) 30)
                .deadlineRemindBefore((short) 1440)
                .examRemindBeforeDays((short) 2)
                .build();

        newUser.setSettings(settings);
        return newUser;
    }

    /**
     * Lấy danh sách tất cả user cùng cài đặt thông báo (dùng cho scheduler).
     */
    @Transactional(readOnly = true)
    public List<Map<String, Object>> getAllWithNotifications() {
        return userRepository.findAll().stream()
                .filter(User::getIsActive)
                .map(user -> {
                    Map<String, Object> map = new HashMap<>();
                    map.put("telegramId", user.getTelegramId());
                    UserSettings settings = user.getSettings();
                    if (settings != null) {
                        map.put("notifications", NotificationSettingsResponse.from(settings));
                    } else {
                        map.put("notifications", null);
                    }
                    return map;
                })
                .toList();
    }
}
