package com.studybot.exam;

import com.studybot.user.User;
import com.studybot.user.UserRepository;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.time.LocalDate;
import java.time.LocalTime;
import java.time.format.DateTimeFormatter;
import java.util.List;

@Service
@RequiredArgsConstructor
@Slf4j
public class ExamService {

    private final ExamRepository examRepository;
    private final UserRepository userRepository;

    public List<Exam> getExams(Long telegramId) {
        User user = getUser(telegramId);
        return examRepository.findByUserOrderByExamDateAscStartTimeAsc(user);
    }

    @Transactional
    public Exam addExam(Long telegramId, String subject, String examDateStr,
                        String startTimeStr, String room, String examType) {
        User user = getUser(telegramId);

        LocalDate examDate;
        try {
            examDate = LocalDate.parse(examDateStr);
        } catch (Exception e) {
            throw new IllegalArgumentException(
                "Ngày thi không hợp lệ: '" + examDateStr + "'. Dùng YYYY-MM-DD");
        }

        LocalTime startTime;
        try {
            startTime = LocalTime.parse(startTimeStr, DateTimeFormatter.ofPattern("H:mm"));
        } catch (Exception e) {
            try {
                startTime = LocalTime.parse(startTimeStr);
            } catch (Exception e2) {
                throw new IllegalArgumentException(
                    "Giờ thi không hợp lệ: '" + startTimeStr + "'. Dùng HH:MM");
            }
        }

        Exam exam = Exam.builder()
                .user(user)
                .subject(subject.trim())
                .examDate(examDate)
                .startTime(startTime)
                .room(room != null && !room.isBlank() ? room.trim() : null)
                .examType(examType != null && !examType.isBlank() ? examType.trim() : null)
                .build();

        exam = examRepository.save(exam);
        log.info("✅ User {} thêm lịch thi: '{}' ngày {}", telegramId, subject, examDate);
        return exam;
    }

    private User getUser(Long telegramId) {
        return userRepository.findByTelegramId(telegramId)
                .orElseThrow(() -> new RuntimeException(
                        "User chưa đăng ký. Vui lòng dùng /start trước."));
    }
}
