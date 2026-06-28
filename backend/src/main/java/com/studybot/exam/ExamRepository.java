package com.studybot.exam;

import com.studybot.user.User;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.List;

@Repository
public interface ExamRepository extends JpaRepository<Exam, Long> {

    /** Lấy tất cả lịch thi của user, sắp xếp theo ngày thi gần nhất. */
    List<Exam> findByUserOrderByExamDateAscStartTimeAsc(User user);
}
