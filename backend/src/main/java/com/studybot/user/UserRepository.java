package com.studybot.user;

import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.Optional;

/**
 * Repository cho bảng "users".
 *
 * JpaRepository<User, Long> tự động cung cấp:
 *   save(user)     → INSERT hoặc UPDATE
 *   findById(id)   → SELECT WHERE id = ?
 *   findAll()      → SELECT *
 *   delete(user)   → DELETE
 *   count()        → SELECT COUNT(*)
 *
 * Khai báo method tên đặc biệt → Spring tự tạo SQL.
 */
@Repository
public interface UserRepository extends JpaRepository<User, Long> {

    /**
     * Tìm user theo Telegram ID.
     * SQL: SELECT * FROM users WHERE telegram_id = ?
     */
    Optional<User> findByTelegramId(Long telegramId);

    /**
     * Kiểm tra user đã tồn tại chưa.
     * SQL: SELECT COUNT(*) > 0 FROM users WHERE telegram_id = ?
     */
    boolean existsByTelegramId(Long telegramId);
}
