package com.studybot.schedule;

import com.studybot.user.User;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.List;
import java.util.Optional;

/**
 * Repository cho bảng "subjects".
 */
@Repository
public interface SubjectRepository extends JpaRepository<Subject, Long> {

    /** Lấy tất cả môn học đang active của 1 user. */
    List<Subject> findByUserAndIsActiveTrue(User user);

    /** Tìm môn học theo mã môn + user (để upsert khi sync sheet). */
    Optional<Subject> findByUserAndCode(User user, String code);

    /** Tìm môn học theo tên + user (fallback khi không có mã môn). */
    Optional<Subject> findByUserAndName(User user, String name);

    /** Xóa tất cả môn học (và cascade class_schedules) của 1 user trước khi sync. */
    void deleteAllByUser(User user);
}
