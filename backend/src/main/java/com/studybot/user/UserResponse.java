package com.studybot.user;

import lombok.Getter;
import lombok.Setter;
import lombok.NoArgsConstructor;

/**
 * DTO trả về thông tin user cho Python Bot.
 *
 * API trả JSON:
 * {
 *   "id":          1,
 *   "telegramId":  123456789,
 *   "username":    "phuongdev",
 *   "fullName":    "Phương Dev",
 *   "isActive":    true,
 *   "createdAt":   "2025-06-07T16:46:12"
 * }
 */
@Getter
@Setter
@NoArgsConstructor
public class UserResponse {

    private Long    id;
    private Long    telegramId;
    private String  username;
    private String  fullName;
    private String  languageCode;
    private String  timezone;
    private Boolean isActive;
    private String  createdAt;   // ISO string — tránh Jackson LocalDateTime issue

    /**
     * Static factory — tạo UserResponse từ User entity.
     */
    public static UserResponse from(User user) {
        UserResponse res = new UserResponse();
        res.setId(user.getId());
        res.setTelegramId(user.getTelegramId());
        res.setUsername(user.getUsername());
        res.setFullName(user.getFullName());
        res.setLanguageCode(user.getLanguageCode());
        res.setTimezone(user.getTimezone());
        res.setIsActive(user.getIsActive());
        res.setCreatedAt(user.getCreatedAt() != null
                ? user.getCreatedAt().toString() : null);
        return res;
    }
}
