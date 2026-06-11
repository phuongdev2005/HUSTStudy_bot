package com.studybot.user;

import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotNull;
import lombok.Getter;
import lombok.Setter;

/**
 * DTO nhận request đăng ký / cập nhật user.
 *
 * Python Bot gửi JSON:
 * {
 *   "telegramId": 123456789,
 *   "username":   "phuongdev",
 *   "fullName":   "Phương Dev"
 * }
 */
@Getter
@Setter
public class UserRequest {

    @NotNull(message = "telegramId không được để trống")
    private Long telegramId;

    private String username;          // Có thể null

    @NotBlank(message = "fullName không được để trống")
    private String fullName;

    private String languageCode = "vi";

    private String timezone = "Asia/Ho_Chi_Minh";
}
