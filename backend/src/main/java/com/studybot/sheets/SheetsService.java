package com.studybot.sheets;

import com.google.api.services.sheets.v4.Sheets;
import com.google.api.services.sheets.v4.model.ValueRange;
import com.studybot.schedule.ClassScheduleRepository;
import com.studybot.schedule.ClassSession;
import com.studybot.schedule.DailyActivity;
import com.studybot.schedule.DailyActivityRepository;
import com.studybot.schedule.Subject;
import com.studybot.schedule.SubjectRepository;
import com.studybot.user.User;
import com.studybot.user.UserRepository;
import com.studybot.user.UserSettings;
import com.studybot.user.UserSettingsRepository;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.io.IOException;
import java.time.LocalDateTime;
import java.util.ArrayList;
import java.util.List;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

/**
 * Service xử lý Google Sheets:
 *  1. Lưu / cập nhật link sheet của user
 *  2. Đọc dữ liệu từ sheet → parse → upsert vào DB
 *
 * ──────────────────────────────────────────────────────────────
 * FORMAT GOOGLE SHEET (hàng 1 = header, từ hàng 2 trở đi = data):
 *
 *  Cột A | Cột B  | Cột C      | Cột D     | Cột E   | Cột F   | Cột G
 *  Tên môn | Mã môn | Thứ (2-8) | Giờ bắt đầu | Giờ kết | Phòng | Giảng viên
 *
 * Ví dụ:
 *  Giải tích 1 | MA1010 | 2 | 07:00 | 09:30 | B1-301 | Nguyễn A
 *  Lập trình   | IT3080 | 4 | 13:00 | 15:30 | C9-201 | Trần B
 * ──────────────────────────────────────────────────────────────
 */
@Service
@Slf4j
@RequiredArgsConstructor
public class SheetsService {

    private final Sheets sheetsClient;          // Có thể null nếu chưa có credentials
    private final UserRepository userRepository;
    private final UserSettingsRepository userSettingsRepository;
    private final SubjectRepository subjectRepository;
    private final ClassScheduleRepository classScheduleRepository;
    private final DailyActivityRepository dailyActivityRepository;

    // Regex trích spreadsheetId từ URL Google Sheets
    private static final Pattern SHEET_ID_PATTERN =
            Pattern.compile("/spreadsheets/d/([a-zA-Z0-9_-]+)");

    // Range đọc dữ liệu: bỏ hàng 1 (header), đọc từ hàng 2
    private static final String DATA_RANGE = "A2:G";

    // ═══════════════════════════════════════════════════════════
    //  1. Lưu link Google Sheet của user
    // ═══════════════════════════════════════════════════════════

    /**
     * Lưu hoặc cập nhật Google Sheet URL của user.
     *
     * @param telegramId  Telegram chat_id của user
     * @param sheetUrl    Link Google Sheet (dạng https://docs.google.com/spreadsheets/d/...)
     * @return Thông báo kết quả
     */
    @Transactional
    public String setSheetUrl(Long telegramId, String sheetUrl) {
        // Validate URL có đúng format Google Sheets không
        String spreadsheetId = extractSpreadsheetId(sheetUrl);
        if (spreadsheetId == null) {
            return "❌ Link không hợp lệ! Vui lòng dùng link Google Sheets đúng định dạng:\n" +
                   "https://docs.google.com/spreadsheets/d/...";
        }

        User user = getUserByTelegramId(telegramId);
        UserSettings settings = getUserSettings(user);

        settings.setGoogleSheetUrl(sheetUrl);
        userSettingsRepository.save(settings);

        log.info("✅ User {} đã cập nhật Google Sheet: {}", telegramId, spreadsheetId);
        return "✅ Đã lưu Google Sheet của bạn!\n\n" +
               "📋 Sheet ID: `" + spreadsheetId + "`\n\n" +
               "Dùng /syncsheet để đồng bộ thời khóa biểu từ sheet vào bot.";
    }

    // ═══════════════════════════════════════════════════════════
    //  2. Đồng bộ dữ liệu từ sheet vào DB
    // ═══════════════════════════════════════════════════════════

    /**
     * Đọc Google Sheet của user → parse → upsert vào DB.
     *
     * @param telegramId Telegram chat_id
     * @return SyncResult chứa thông tin kết quả sync
     */
    @Transactional
    public SyncResult syncScheduleFromSheet(Long telegramId) {
        // Kiểm tra Sheets API có khả dụng không
        if (sheetsClient == null) {
            return SyncResult.error("Google Sheets API chưa được cấu hình trên server.");
        }

        User user = getUserByTelegramId(telegramId);
        UserSettings settings = getUserSettings(user);

        String sheetUrl = settings.getGoogleSheetUrl();
        if (sheetUrl == null || sheetUrl.isBlank()) {
            return SyncResult.error(
                "Bạn chưa liên kết Google Sheet!\n" +
                "Dùng lệnh: /setsheet <link sheet của bạn>");
        }

        String spreadsheetId = extractSpreadsheetId(sheetUrl);
        if (spreadsheetId == null) {
            return SyncResult.error("Link sheet không hợp lệ. Dùng /setsheet để cập nhật link mới.");
        }

        try {
            // Đọc dữ liệu từ Google Sheets API
            ValueRange response = sheetsClient.spreadsheets().values()
                    .get(spreadsheetId, DATA_RANGE)
                    .execute();

            List<List<Object>> rows = response.getValues();
            if (rows == null || rows.isEmpty()) {
                return SyncResult.error(
                    "Sheet trống hoặc chưa có dữ liệu từ hàng 2 trở đi.\n" +
                    "Kiểm tra lại format: hàng 1 = header, từ hàng 2 = dữ liệu.");
            }

            // Xóa toàn bộ môn học cũ của user (cascade → xóa cả class_schedules)
            subjectRepository.deleteAllByUser(user);
            subjectRepository.flush();

            // Parse và lưu dữ liệu mới
            List<String> errors = new ArrayList<>();
            int successCount = 0;

            for (int i = 0; i < rows.size(); i++) {
                List<Object> row = rows.get(i);
                int rowNum = i + 2; // Hàng thực tế trong sheet (1-indexed, bỏ header)

                try {
                    parseAndSaveRow(row, user, rowNum);
                    successCount++;
                } catch (Exception e) {
                    errors.add("Hàng " + rowNum + ": " + e.getMessage());
                    log.warn("Lỗi parse hàng {} của user {}: {}", rowNum, telegramId, e.getMessage());
                }
            }

            // Cập nhật thời gian sync
            settings.setSheetSyncedAt(LocalDateTime.now());
            userSettingsRepository.save(settings);

            log.info("✅ Sync sheet xong cho user {} – {} buổi học, {} lỗi",
                     telegramId, successCount, errors.size());

            return SyncResult.success(successCount, errors);

        } catch (IOException e) {
            log.error("Lỗi đọc Google Sheet {} của user {}: {}", spreadsheetId, telegramId, e.getMessage());

            if (e.getMessage() != null && e.getMessage().contains("403")) {
                return SyncResult.error(
                    "❌ Không có quyền đọc sheet!\n\n" +
                    "Vui lòng set sheet thành *'Anyone with the link can view'*:\n" +
                    "Sheet → Share → Change to Anyone with the link → Viewer");
            }
            if (e.getMessage() != null && e.getMessage().contains("404")) {
                return SyncResult.error("❌ Không tìm thấy sheet. Kiểm tra lại link bằng /setsheet.");
            }
            return SyncResult.error("❌ Lỗi kết nối Google Sheets: " + e.getMessage());
        }
    }

    // ═══════════════════════════════════════════════════════════
    //  3. Lấy lịch học (để bot hiển thị)
    // ═══════════════════════════════════════════════════════════

    /**
     * Lấy lịch học hôm nay của user từ DB.
     * dayOfWeek: 1=T2, 2=T3, 3=T4, 4=T5, 5=T6, 6=T7, 7=CN
     */
    public List<ScheduleItem> getTodaySchedule(Long telegramId) {
        User user = getUserByTelegramId(telegramId);
        // Tính dayOfWeek theo convention của DB (1=T2 … 7=CN)
        int javaDow = java.time.LocalDate.now().getDayOfWeek().getValue(); // 1=Mon … 7=Sun
        List<ClassSession> sessions = classScheduleRepository
                .findTodayByUserId(user.getId(), javaDow);
        return sessions.stream().map(ScheduleItem::from).toList();
    }

    /**
     * Lấy toàn bộ lịch học trong tuần của user từ DB.
     */
    public List<ScheduleItem> getWeeklySchedule(Long telegramId) {
        User user = getUserByTelegramId(telegramId);
        List<ClassSession> sessions = classScheduleRepository
                .findWeeklyByUserId(user.getId());
        return sessions.stream().map(ScheduleItem::from).toList();
    }

    // ═══════════════════════════════════════════════════════════
    //  Private helpers
    // ═══════════════════════════════════════════════════════════

    /**
     * Parse 1 dòng sheet và lưu vào DB.
     * Format: [Tên môn, Mã môn, Thứ, Giờ bắt đầu, Giờ kết, Phòng, Giảng viên]
     */
    private void parseAndSaveRow(List<Object> row, User user, int rowNum) {
        if (row.size() < 5) {
            throw new IllegalArgumentException("Cần ít nhất 5 cột (Tên môn, Mã môn, Thứ, Giờ bắt, Giờ kết)");
        }

        String name      = getString(row, 0);
        String code      = getString(row, 1);
        String dayStr    = getString(row, 2);
        String startTime = getString(row, 3);
        String endTime   = getString(row, 4);
        String room      = row.size() > 5 ? getString(row, 5) : null;
        String teacher   = row.size() > 6 ? getString(row, 6) : null;

        if (name.isBlank()) throw new IllegalArgumentException("Tên môn không được để trống");
        if (startTime.isBlank() || endTime.isBlank())
            throw new IllegalArgumentException("Giờ học không được để trống");

        int dayOfWeek = parseDayOfWeek(dayStr);

        // Tạo hoặc tìm Subject
        Subject subject = Subject.builder()
                .user(user)
                .name(name.trim())
                .code(code.isBlank() ? null : code.trim())
                .teacher(teacher != null && !teacher.isBlank() ? teacher.trim() : null)
                .isActive(true)
                .build();
        subject = subjectRepository.save(subject);

        // Tạo ClassSession
        ClassSession session = ClassSession.builder()
                .subject(subject)
                .dayOfWeek(dayOfWeek)
                .startTime(startTime.trim())
                .endTime(endTime.trim())
                .room(room != null && !room.isBlank() ? room.trim() : null)
                .weekType("ALL")
                .build();
        classScheduleRepository.save(session);
    }

    /**
     * Chuyển chuỗi ngày thành số (1=T2, 2=T3, …, 7=CN).
     * Chấp nhận: "2", "T2", "Thứ 2", "Monday", "Mon" ...
     */
    private int parseDayOfWeek(String raw) {
        if (raw == null || raw.isBlank()) throw new IllegalArgumentException("Thứ không được để trống");
        String s = raw.trim().toLowerCase()
                .replace("thứ", "").replace("thu", "")
                .replace(" ", "").replace("_", "");

        return switch (s) {
            case "2", "hai", "t2", "monday",    "mon" -> 1;
            case "3", "ba",  "t3", "tuesday",   "tue" -> 2;
            case "4", "tu",  "t4", "wednesday", "wed" -> 3;
            case "5", "nam", "t5", "thursday",  "thu" -> 4;
            case "6", "sau", "t6", "friday",    "fri" -> 5;
            case "7", "bay", "t7", "saturday",  "sat" -> 6;
            case "8", "cn",       "sunday",     "sun" -> 7;
            default -> throw new IllegalArgumentException("Thứ không hợp lệ: '" + raw + "' (dùng 2-8 hoặc T2-CN)");
        };
    }

    private String getString(List<Object> row, int index) {
        if (index >= row.size() || row.get(index) == null) return "";
        return row.get(index).toString().trim();
    }

    /** Trích spreadsheetId từ URL Google Sheets. */
    public static String extractSpreadsheetId(String url) {
        if (url == null || url.isBlank()) return null;
        Matcher m = SHEET_ID_PATTERN.matcher(url);
        return m.find() ? m.group(1) : null;
    }

    private User getUserByTelegramId(Long telegramId) {
        return userRepository.findByTelegramId(telegramId)
                .orElseThrow(() -> new RuntimeException(
                        "User chưa đăng ký. Vui lòng dùng /start trước."));
    }

    private UserSettings getUserSettings(User user) {
        return userSettingsRepository.findByUser(user)
                .orElseThrow(() -> new RuntimeException(
                        "Không tìm thấy settings của user " + user.getTelegramId()));
    }

    // ═══════════════════════════════════════════════════════════
    //  DAILY ACTIVITIES – Lịch sinh hoạt toàn ngày
    // ═══════════════════════════════════════════════════════════

    /**
     * Đọc Google Sheet format 6 cột → sync vào bảng daily_activities.
     *
     * FORMAT (hàng 1 = header, từ hàng 2 = data):
     *  Cột A     | Cột B   | Cột C   | Cột D              | Cột E      | Cột F
     *  Thứ       | Bắt đầu | Kết thúc| Hoạt động          | Danh mục   | Ghi chú
     *  Tất cả    | 00:00   | 06:30   | Ngủ                | Nghỉ ngơi  |
     *  2         | 07:30   | 09:30   | Giải tích 1        | Học tập    | B1-301
     */
    @Transactional
    public SyncResult syncDailyScheduleFromSheet(Long telegramId) {
        if (sheetsClient == null) {
            return SyncResult.error("Google Sheets API chưa được cấu hình trên server.");
        }

        User user = getUserByTelegramId(telegramId);
        UserSettings settings = getUserSettings(user);

        String sheetUrl = settings.getGoogleSheetUrl();
        if (sheetUrl == null || sheetUrl.isBlank()) {
            return SyncResult.error(
                "Bạn chưa liên kết Google Sheet!\n" +
                "Dùng lệnh: /setsheet <link sheet của bạn>");
        }

        String spreadsheetId = extractSpreadsheetId(sheetUrl);
        if (spreadsheetId == null) {
            return SyncResult.error("Link sheet không hợp lệ. Dùng /setsheet để cập nhật link mới.");
        }

        try {
            ValueRange response = sheetsClient.spreadsheets().values()
                    .get(spreadsheetId, "A2:F")
                    .execute();

            List<List<Object>> rows = response.getValues();
            if (rows == null || rows.isEmpty()) {
                return SyncResult.error(
                    "Sheet trống hoặc chưa có dữ liệu từ hàng 2.\n" +
                    "Format: Thứ | Giờ bắt | Giờ kết | Hoạt động | Danh mục | Ghi chú");
            }

            // Xóa toàn bộ lịch cũ của user
            dailyActivityRepository.deleteAllByUser(user);
            dailyActivityRepository.flush();

            List<String> errors = new ArrayList<>();
            int successCount = 0;

            for (int i = 0; i < rows.size(); i++) {
                List<Object> row = rows.get(i);
                int rowNum = i + 2;
                try {
                    parseDailyRow(row, user, i);
                    successCount++;
                } catch (Exception e) {
                    errors.add("Hàng " + rowNum + ": " + e.getMessage());
                    log.warn("Lỗi parse hàng {} daily của user {}: {}", rowNum, telegramId, e.getMessage());
                }
            }

            settings.setSheetSyncedAt(LocalDateTime.now());
            userSettingsRepository.save(settings);

            log.info("✅ Sync daily schedule xong user {} – {} hoạt động, {} lỗi",
                     telegramId, successCount, errors.size());

            return SyncResult.success(successCount, errors);

        } catch (java.io.IOException e) {
            log.error("Lỗi đọc Google Sheet {} của user {}: {}", spreadsheetId, telegramId, e.getMessage());
            if (e.getMessage() != null && e.getMessage().contains("403")) {
                return SyncResult.error(
                    "❌ Không có quyền đọc sheet!\n\n" +
                    "Vào sheet → Share → Anyone with the link → Viewer");
            }
            return SyncResult.error("❌ Lỗi kết nối Google Sheets: " + e.getMessage());
        }
    }

    /**
     * Lấy lịch sinh hoạt của 1 ngày cụ thể (kết hợp "Tất cả" + ngày đó).
     * dayOfWeek: 1=T2 … 7=CN (theo Java DayOfWeek.getValue())
     */
    public List<DailyActivityItem> getDailyActivities(Long telegramId, Integer dayOfWeek) {
        User user = getUserByTelegramId(telegramId);
        return dailyActivityRepository
                .findDayActivities(user.getId(), dayOfWeek)
                .stream()
                .map(DailyActivityItem::from)
                .toList();
    }

    /**
     * Lấy toàn bộ lịch sinh hoạt của user (tất cả các ngày).
     */
    public List<DailyActivityItem> getAllDailyActivities(Long telegramId) {
        User user = getUserByTelegramId(telegramId);
        return dailyActivityRepository
                .findAllByUserId(user.getId())
                .stream()
                .map(DailyActivityItem::from)
                .toList();
    }

    /**
     * Parse 1 dòng sheet sang DailyActivity.
     * Format: [Thứ, Giờ bắt, Giờ kết, Hoạt động, Danh mục, Ghi chú]
     */
    private void parseDailyRow(List<Object> row, User user, int sortOrder) {
        if (row.size() < 4) {
            throw new IllegalArgumentException("Cần ít nhất 4 cột: Thứ, Giờ bắt, Giờ kết, Hoạt động");
        }

        String dayStr      = getString(row, 0);
        String startTime   = getString(row, 1);
        String endTime     = getString(row, 2);
        String activity    = getString(row, 3);
        String category    = row.size() > 4 ? getString(row, 4) : "Khác";
        String note        = row.size() > 5 ? getString(row, 5) : null;

        if (startTime.isBlank() || endTime.isBlank()) {
            throw new IllegalArgumentException("Giờ bắt đầu/kết thúc không được để trống");
        }
        if (activity.isBlank()) {
            throw new IllegalArgumentException("Tên hoạt động không được để trống");
        }

        // dayOfWeek: null = mọi ngày
        Integer dayOfWeek = parseDayOfWeekNullable(dayStr);

        // Normalize category
        String cat = normalizeCategory(category);

        DailyActivity da = DailyActivity.builder()
                .user(user)
                .dayOfWeek(dayOfWeek)
                .startTime(startTime.trim())
                .endTime(endTime.trim())
                .activity(activity.trim())
                .category(cat)
                .note(note != null && !note.isBlank() ? note.trim() : null)
                .sortOrder(sortOrder)
                .build();

        dailyActivityRepository.save(da);
    }

    /**
     * Parse chuỗi Thứ, trả về null nếu là "Tất cả" / "all" / để trống.
     */
    private Integer parseDayOfWeekNullable(String raw) {
        if (raw == null || raw.isBlank()) return null;
        String s = raw.trim().toLowerCase()
                .replace("tất cả", "all")
                .replace("tat ca", "all")
                .replace("mọi ngày", "all")
                .replace("everyday", "all")
                .replace("daily", "all");

        if (s.equals("all") || s.equals("*")) return null;  // mọi ngày

        // Tái dùng parseDayOfWeek từ logic cũ
        s = s.replace("thứ", "").replace("thu", "")
             .replace(" ", "").replace("_", "");
        return switch (s) {
            case "2", "hai", "t2", "monday",    "mon" -> 1;
            case "3", "ba",  "t3", "tuesday",   "tue" -> 2;
            case "4", "tu",  "t4", "wednesday", "wed" -> 3;
            case "5", "nam", "t5", "thursday"         -> 4;
            case "6", "sau", "t6", "friday",    "fri" -> 5;
            case "7", "bay", "t7", "saturday",  "sat" -> 6;
            case "8", "cn",       "sunday",     "sun" -> 7;
            default -> throw new IllegalArgumentException(
                "Thứ không hợp lệ: '" + raw + "' (dùng 2-8, T2-CN, hoặc 'Tất cả')");
        };
    }

    /**
     * Chuẩn hóa tên danh mục về dạng chuẩn.
     */
    private String normalizeCategory(String raw) {
        if (raw == null || raw.isBlank()) return "Khác";
        String s = raw.trim().toLowerCase();
        if (s.contains("ng") && s.contains("i"))     return "Nghỉ ngơi";
        if (s.contains("sinh ho"))                   return "Sinh hoạt";
        if (s.contains("n") && s.contains("u"))      return "Ăn uống";
        if (s.contains("h") && s.contains("t"))      return "Học tập";
        if (s.contains("th") && s.contains("d"))     return "Thể dục";
        if (s.contains("gi") && s.contains("tr"))    return "Giải trí";
        if (s.contains("di chuy"))                   return "Di chuyển";
        // Nếu user gõ đúng tiếng Việt
        return raw.trim().length() > 30 ? raw.trim().substring(0, 30) : raw.trim();
    }
}

