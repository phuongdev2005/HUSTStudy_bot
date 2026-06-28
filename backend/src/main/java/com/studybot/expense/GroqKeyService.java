package com.studybot.expense;

import com.studybot.user.User;
import com.studybot.user.UserSettings;
import com.studybot.user.UserSettingsRepository;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.time.LocalDate;
import java.util.Optional;

/**
 * Service quản lý Groq API Key cho từng user.
 *
 * Logic ưu tiên:
 *   1. User có key riêng  → dùng key của user (không giới hạn)
 *   2. User chưa có key   → dùng key bot owner (giới hạn FREE_DAILY_LIMIT lần/ngày)
 *   3. Hết quota free     → báo lỗi, hướng dẫn user lấy key riêng
 */
@Service
@RequiredArgsConstructor
@Slf4j
public class GroqKeyService {

    /** Số lượt scan AI miễn phí mỗi ngày khi dùng key bot owner */
    public static final int FREE_DAILY_LIMIT = 10;

    @Value("${groq.api-key:}")
    private String ownerApiKey;   // Key của bot owner (từ .env GROQ_API_KEY)

    private final UserSettingsRepository settingsRepository;

    // ═══════════════════════════════════════════════════════════
    //  Kết quả resolve key
    // ═══════════════════════════════════════════════════════════

    public enum KeySource { USER_KEY, OWNER_FREE }

    public record ResolvedKey(
            String apiKey,
            KeySource source,
            int freeUsesRemaining   // -1 nếu dùng key riêng (không giới hạn)
    ) {}

    // ═══════════════════════════════════════════════════════════
    //  Lấy API key cho user (chưa tốn quota — chỉ check)
    // ═══════════════════════════════════════════════════════════

    /**
     * Kiểm tra và trả về API key user có thể dùng.
     * KHÔNG tốn quota — gọi {@link #consumeFreeQuota(User)} sau khi scan thành công.
     *
     * @throws IllegalStateException nếu user hết quota free và không có key riêng
     */
    public ResolvedKey resolveKey(User user) {
        Optional<UserSettings> settingsOpt = settingsRepository.findByUser(user);
        UserSettings settings = settingsOpt.orElse(null);

        // 1. User có key riêng → dùng luôn
        if (settings != null && settings.getGroqApiKey() != null && !settings.getGroqApiKey().isBlank()) {
            log.debug("User {} dùng Groq key riêng", user.getTelegramId());
            return new ResolvedKey(settings.getGroqApiKey(), KeySource.USER_KEY, -1);
        }

        // 2. Dùng key owner → check quota
        if (ownerApiKey == null || ownerApiKey.isBlank()) {
            throw new IllegalStateException(
                "Bot chưa cấu hình Groq API Key. Liên hệ admin hoặc dùng /setkey để cài key riêng.");
        }

        int usedToday = getUsedToday(settings);
        int remaining = FREE_DAILY_LIMIT - usedToday;

        if (remaining <= 0) {
            throw new IllegalStateException(String.format(
                "🚫 Bạn đã dùng hết %d lượt scan AI miễn phí hôm nay!\n\n" +
                "💡 Để dùng không giới hạn, lấy API key miễn phí tại:\n" +
                "   https://console.groq.com/keys\n" +
                "Sau đó cài vào bot: /setkey <your_key>",
                FREE_DAILY_LIMIT));
        }

        log.debug("User {} dùng key owner, còn {} lượt hôm nay", user.getTelegramId(), remaining);
        return new ResolvedKey(ownerApiKey, KeySource.OWNER_FREE, remaining);
    }

    // ═══════════════════════════════════════════════════════════
    //  Tiêu 1 lượt quota free (gọi sau khi scan thành công)
    // ═══════════════════════════════════════════════════════════

    @Transactional
    public void consumeFreeQuota(User user) {
        UserSettings settings = settingsRepository.findByUser(user)
                .orElseGet(() -> {
                    UserSettings s = new UserSettings();
                    s.setUser(user);
                    return s;
                });

        // Nếu user có key riêng → không tốn quota
        if (settings.getGroqApiKey() != null && !settings.getGroqApiKey().isBlank()) return;

        // Reset counter nếu sang ngày mới
        LocalDate today = LocalDate.now();
        if (settings.getAiFreeUsesDate() == null || !settings.getAiFreeUsesDate().equals(today)) {
            settings.setAiFreeUsesToday((short) 0);
            settings.setAiFreeUsesDate(today);
        }

        settings.setAiFreeUsesToday((short) (settings.getAiFreeUsesToday() + 1));
        settingsRepository.save(settings);
        log.info("User {} dùng lượt free #{}/{}", user.getTelegramId(),
                settings.getAiFreeUsesToday(), FREE_DAILY_LIMIT);
    }

    // ═══════════════════════════════════════════════════════════
    //  Cài / xóa key riêng của user
    // ═══════════════════════════════════════════════════════════

    @Transactional
    public String setUserKey(User user, String apiKey) {
        UserSettings settings = settingsRepository.findByUser(user)
                .orElseGet(() -> {
                    UserSettings s = new UserSettings();
                    s.setUser(user);
                    return s;
                });

        if (apiKey == null || apiKey.isBlank()) {
            settings.setGroqApiKey(null);
            settingsRepository.save(settings);
            return "✅ Đã xóa Groq API Key của bạn. Sẽ dùng quota miễn phí (" + FREE_DAILY_LIMIT + " lần/ngày).";
        }

        // Validate format cơ bản: Groq key bắt đầu bằng gsk_
        if (!apiKey.startsWith("gsk_") || apiKey.length() < 20) {
            return "❌ Key không hợp lệ. Groq API Key phải bắt đầu bằng `gsk_`.\n" +
                   "Lấy key tại: https://console.groq.com/keys";
        }

        settings.setGroqApiKey(apiKey);
        settingsRepository.save(settings);
        log.info("User {} đã cài Groq API Key riêng", user.getTelegramId());
        return "✅ Đã lưu Groq API Key của bạn!\nTừ giờ scan ảnh không giới hạn số lần.";
    }

    // ═══════════════════════════════════════════════════════════
    //  Lấy trạng thái quota của user
    // ═══════════════════════════════════════════════════════════

    public record KeyStatus(
            boolean hasOwnKey,
            String userKey,
            int usedToday,
            int remaining,
            boolean isUnlimited
    ) {}

    public KeyStatus getStatus(User user) {
        Optional<UserSettings> settingsOpt = settingsRepository.findByUser(user);
        UserSettings settings = settingsOpt.orElse(null);

        boolean hasOwnKey = settings != null
                && settings.getGroqApiKey() != null
                && !settings.getGroqApiKey().isBlank();

        String userKey = hasOwnKey ? settings.getGroqApiKey() : null;

        if (hasOwnKey) {
            return new KeyStatus(true, userKey, 0, -1, true);
        }

        int usedToday = getUsedToday(settings);
        return new KeyStatus(false, null, usedToday, FREE_DAILY_LIMIT - usedToday, false);
    }

    // ═══════════════════════════════════════════════════════════
    //  Private helpers
    // ═══════════════════════════════════════════════════════════

    private int getUsedToday(UserSettings settings) {
        if (settings == null) return 0;
        LocalDate today = LocalDate.now();
        // Nếu ngày khác → coi như chưa dùng lần nào hôm nay
        if (settings.getAiFreeUsesDate() == null || !settings.getAiFreeUsesDate().equals(today)) {
            return 0;
        }
        return settings.getAiFreeUsesToday() != null ? settings.getAiFreeUsesToday() : 0;
    }
}
