package com.studybot.user;

import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;
import java.util.Map;

/**
 * REST Controller cho User API.
 * Python Bot gọi các endpoint này qua HTTP.
 *
 * Base URL: /api/users
 */
@RestController
@RequestMapping("/users")
@RequiredArgsConstructor
public class UserController {

    private final UserService userService;

    /**
     * Đăng ký user mới hoặc cập nhật nếu đã tồn tại.
     *
     * POST /api/users/register
     * Body: { "telegramId": 123456789, "fullName": "Phương Dev" }
     *
     * Response:
     *   201 Created → { "id": 1, "telegramId": 123456789, ... }
     */
    @PostMapping("/register")
    public ResponseEntity<UserResponse> register(@Valid @RequestBody UserRequest request) {
        UserResponse response = userService.registerOrUpdate(request);
        return ResponseEntity.status(201).body(response);
    }

    /**
     * Lấy thông tin user theo Telegram ID.
     *
     * GET /api/users/telegram/{telegramId}
     *
     * Response:
     *   200 OK  → { "id": 1, "fullName": "Phương Dev", ... }
     *   404     → Nếu không tìm thấy
     */
    @GetMapping("/telegram/{telegramId}")
    public ResponseEntity<UserResponse> getByTelegramId(@PathVariable Long telegramId) {
        return ResponseEntity.ok(userService.getByTelegramId(telegramId));
    }

    /**
     * Kiểm tra user đã tồn tại chưa.
     *
     * GET /api/users/exists/{telegramId}
     *
     * Response: 200 OK → true hoặc false
     */
    @GetMapping("/exists/{telegramId}")
    public ResponseEntity<Boolean> exists(@PathVariable Long telegramId) {
        return ResponseEntity.ok(userService.existsByTelegramId(telegramId));
    }
    /**
     * Lấy cài đặt thông báo hiện tại của user.
     *
     * GET /api/users/{telegramId}/notifications
     */
    @GetMapping("/{telegramId}/notifications")
    public ResponseEntity<NotificationSettingsResponse> getNotifications(
            @PathVariable Long telegramId) {
        return ResponseEntity.ok(userService.getNotificationSettings(telegramId));
    }

    /**
     * Cập nhật cài đặt thông báo (chỉ fields nào có trong body mới được update).
     *
     * PATCH /api/users/{telegramId}/notifications
     * Body: { "notifyDailySummary": true, "dailySummaryTime": "06:30" }
     */
    @PatchMapping("/{telegramId}/notifications")
    public ResponseEntity<NotificationSettingsResponse> updateNotifications(
            @PathVariable Long telegramId,
            @RequestBody NotificationSettingsRequest request) {
        request.setTelegramId(telegramId);
        return ResponseEntity.ok(userService.updateNotificationSettings(request));
    }

    /**
     * User block bot → đánh dấu isActive = false (dừng gửi thông báo).
     *
     * PATCH /api/users/{telegramId}/deactivate
     * Response: 204 No Content
     */
    @PatchMapping("/{telegramId}/deactivate")
    public ResponseEntity<Void> deactivate(@PathVariable Long telegramId) {
        userService.deactivate(telegramId);
        return ResponseEntity.noContent().build();
    }

    /**
     * User unblock / /start lại → đánh dấu isActive = true.
     * (Thường registerOrUpdate đã xử lý, endpoint này để dùng riêng nếu cần.)
     *
     * PATCH /api/users/{telegramId}/activate
     * Response: 204 No Content
     */
    @PatchMapping("/{telegramId}/activate")
    public ResponseEntity<Void> activate(@PathVariable Long telegramId) {
        userService.activate(telegramId);
        return ResponseEntity.noContent().build();
    }

    /**
     * Lấy danh sách tất cả user cùng notification settings (cho scheduler).
     *
     * GET /api/users/all-with-notifications
     */
    @GetMapping("/all-with-notifications")
    public ResponseEntity<List<Map<String, Object>>> getAllWithNotifications() {
        return ResponseEntity.ok(userService.getAllWithNotifications());
    }
}
