package com.studybot.user;

import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.Optional;

/**
 * Repository cho bảng "user_settings".
 */
@Repository
public interface UserSettingsRepository extends JpaRepository<UserSettings, Long> {

    /** Lấy settings theo User entity. */
    Optional<UserSettings> findByUser(User user);

    /** Lấy settings theo userId. */
    Optional<UserSettings> findByUserId(Long userId);
}
