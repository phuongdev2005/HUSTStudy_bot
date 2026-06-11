package com.studybot.user;

import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

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
}
