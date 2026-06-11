package com.studybot.sheets;

import org.springframework.stereotype.Service;
import lombok.extern.slf4j.Slf4j;

/**
 * Service xuất dữ liệu ra Google Sheets.
 *
 * Luồng hoạt động:
 *   1. Python Bot gửi request /export → Java API
 *   2. SheetsService lấy dữ liệu từ DB
 *   3. Ghi vào Google Sheets qua Google Sheets API
 *   4. Trả về URL sheet cho Python Bot
 */
@Service
@Slf4j
public class SheetsService {

    // TODO: Inject Google Sheets API client (SheetsConfig)

    /**
     * Xuất toàn bộ thời khóa biểu ra sheet "Lịch học".
     *
     * @param userId    ID user trong hệ thống
     * @param sheetId   Google Spreadsheet ID
     * @return URL của Google Sheet
     */
    public String exportSchedule(Long userId, String sheetId) {
        // TODO: Lấy dữ liệu từ SubjectRepository + ClassSessionRepository
        //       → Ghi vào sheet "Lịch học"
        log.info("Xuất thời khóa biểu cho user {}", userId);
        return "https://docs.google.com/spreadsheets/d/" + sheetId;
    }

    /**
     * Xuất deadline & lịch thi ra sheet "Deadline & Thi".
     */
    public String exportDeadlineAndExam(Long userId, String sheetId) {
        // TODO: Lấy Deadline + Exam → ghi vào sheet
        log.info("Xuất deadline & lịch thi cho user {}", userId);
        return "https://docs.google.com/spreadsheets/d/" + sheetId;
    }

    /**
     * Xuất báo cáo chi tiêu tháng ra sheet "Chi tiêu".
     */
    public String exportExpenseReport(Long userId, String sheetId, int month, int year) {
        // TODO: Tổng hợp Transaction theo danh mục → ghi bảng tổng hợp vào sheet
        log.info("Xuất báo cáo chi tiêu {}/{} cho user {}", month, year, userId);
        return "https://docs.google.com/spreadsheets/d/" + sheetId;
    }

    /**
     * Xuất toàn bộ dữ liệu (schedule + deadline + exam + expense).
     */
    public String exportAll(Long userId, String sheetId) {
        exportSchedule(userId, sheetId);
        exportDeadlineAndExam(userId, sheetId);
        exportExpenseReport(userId, sheetId,
            java.time.LocalDate.now().getMonthValue(),
            java.time.LocalDate.now().getYear());
        return "https://docs.google.com/spreadsheets/d/" + sheetId;
    }
}
