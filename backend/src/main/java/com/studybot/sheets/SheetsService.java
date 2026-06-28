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
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.beans.factory.annotation.Qualifier;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.io.IOException;
import java.time.LocalDate;
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
public class SheetsService {

    @Qualifier("sheetsClient")
    @Autowired(required = false)       // null nếu chưa có credentials
    private Sheets sheetsClient;

    private final UserRepository userRepository;
    private final UserSettingsRepository userSettingsRepository;
    private final SubjectRepository subjectRepository;
    private final ClassScheduleRepository classScheduleRepository;
    private final DailyActivityRepository dailyActivityRepository;

    @Autowired
    public SheetsService(UserRepository userRepository,
                         UserSettingsRepository userSettingsRepository,
                         SubjectRepository subjectRepository,
                         ClassScheduleRepository classScheduleRepository,
                         DailyActivityRepository dailyActivityRepository) {
        this.userRepository            = userRepository;
        this.userSettingsRepository    = userSettingsRepository;
        this.subjectRepository         = subjectRepository;
        this.classScheduleRepository   = classScheduleRepository;
        this.dailyActivityRepository   = dailyActivityRepository;
    }

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
            // Đọc toàn bộ dữ liệu (kể cả header row)
            ValueRange response = sheetsClient.spreadsheets().values()
                    .get(spreadsheetId, "A1:ZZ")
                    .execute();

            List<List<Object>> rows = response.getValues();
            if (rows == null || rows.isEmpty()) {
                return SyncResult.error("Sheet trống hoặc chưa có dữ liệu.");
            }

            // Auto-detect format dựa vào header row
            List<Object> header = rows.get(0);
            boolean isGridFormat = isGridFormat(header);

            log.info("User {} – detect format: {}", telegramId, isGridFormat ? "GRID (T2-CN cols)" : "ROW (mỗi hàng 1 môn)");

            subjectRepository.deleteAllByUser(user);
            subjectRepository.flush();

            List<String> errors = new ArrayList<>();
            int successCount;

            if (isGridFormat) {
                // Format mới: hàng = ca học, cột = thứ T2..CN
                successCount = parseGridSheet(rows, user, errors);
            } else {
                // Format cũ: mỗi hàng = 1 buổi học
                successCount = parseRowSheet(rows, user, errors);
            }

            settings.setSheetSyncedAt(LocalDateTime.now());
            userSettingsRepository.save(settings);

            log.info("✅ Sync sheet xong cho user {} – {} buổi học, {} lỗi",
                     telegramId, successCount, errors.size());
            return SyncResult.success(successCount, errors);

        } catch (IllegalArgumentException e) {
            log.warn("Lỗi cấu hình dữ liệu khi sync sheet của user {}: {}", telegramId, e.getMessage());
            return SyncResult.error("❌ " + e.getMessage());
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

    private record HeaderInfo(Integer dayOfWeek, LocalDate date) {}

    private HeaderInfo parseHeader(String headerVal) {
        if (headerVal == null || headerVal.isBlank()) return null;
        String s = headerVal.trim().toLowerCase();

        // 1. Kiểm tra định dạng ngày: d/M/yyyy hoặc d/M/yy (hoặc gạch ngang)
        if (s.matches("\\d{1,2}[/\\-]\\d{1,2}[/\\-]\\d{2,4}")) {
            try {
                String normalized = s.replace("-", "/");
                java.time.format.DateTimeFormatter formatter =
                    new java.time.format.DateTimeFormatterBuilder()
                        .appendPattern("[d/M/yyyy]")
                        .appendPattern("[dd/MM/yyyy]")
                        .appendPattern("[d/M/yy]")
                        .appendPattern("[dd/MM/yy]")
                        .toFormatter();
                LocalDate date = LocalDate.parse(normalized, formatter);
                int dow = date.getDayOfWeek().getValue(); // 1 = Mon ... 7 = Sun
                return new HeaderInfo(dow, date);
            } catch (Exception e) {
                log.warn("Lỗi parse date từ header: {} | {}", headerVal, e.getMessage());
            }
        }

        // 2. Định dạng thứ thông thường
        String cleaned = s.replace("thứ", "").replace("thu", "").replace(" ", "");
        Integer dow = switch (cleaned) {
            case "2", "t2", "hai", "monday", "mon" -> 1;
            case "3", "t3", "ba", "tuesday", "tue" -> 2;
            case "4", "t4", "tu", "wednesday", "wed" -> 3;
            case "5", "t5", "nam", "thursday", "thu" -> 4;
            case "6", "t6", "sau", "friday", "fri" -> 5;
            case "7", "t7", "bay", "saturday", "sat" -> 6;
            case "8", "cn", "chủnhật", "chunhat", "sunday", "sun" -> 7;
            default -> null;
        };

        if (dow != null) {
            return new HeaderInfo(dow, null);
        }
        return null;
    }

    /**
     * Nhận diện format sheet dựa vào header row.
     * Grid format: header[1] chứa "T2", "Thứ 2", "2" (ngày trong tuần) hoặc ngày cụ thể.
     */
    private boolean isGridFormat(List<Object> header) {
        if (header == null || header.size() < 2) return false;
        String col1 = header.get(1).toString();
        return parseHeader(col1) != null;
    }

    /**
     * Parse format LƯỚI (grid):
     *   Hàng 1 (header): Ca học | Thứ 2 | Thứ 3 | Thứ 4 | Thứ 5 | Thứ 6 | Thứ 7 | CN (hoặc ngày tháng)
     *   Hàng 2+:         07:00-09:30 | Tên môn|Mã|Phòng|GV | ...  (mỗi ô = 1 môn hoặc trống)
     *
     * Mỗi ô cell format: "Tên môn|Mã môn|Phòng|Giảng viên"  (| là dấu phân cách)
     * Ô trống = không có môn vào ca đó.
     */
    private int parseGridSheet(List<List<Object>> rows, User user, List<String> errors) {
        List<Object> header = rows.get(0);
        HeaderInfo[] colInfos = new HeaderInfo[header.size()];
        java.util.Set<LocalDate> dateSet = new java.util.HashSet<>();
        for (int col = 1; col < header.size(); col++) {
            HeaderInfo info = parseHeader(getString(header, col));
            if (info != null) {
                if (info.date() != null) {
                    if (dateSet.contains(info.date())) {
                        throw new IllegalArgumentException("Trùng lặp ngày " + getString(header, col) + " ở các cột khác nhau. Vui lòng kiểm tra lại sheet!");
                    }
                    dateSet.add(info.date());
                }
                colInfos[col] = info;
            }
        }
        int successCount = 0;

        for (int i = 1; i < rows.size(); i++) {          // bỏ header row
            List<Object> row = rows.get(i);
            if (row == null || row.isEmpty()) continue;

            String timeSlot = getString(row, 0).trim();  // VD: "07:00-09:30"
            if (timeSlot.isBlank()) continue;

            // Parse giờ từ time slot
            String startTime, endTime;
            try {
                String[] times = timeSlot.split("[-–]");  // hỗ trợ cả "-" và "–"
                startTime = times[0].trim();
                endTime   = times[1].trim();
            } catch (Exception e) {
                errors.add("Hàng " + (i + 1) + ": Ca học '" + timeSlot + "' không đúng định dạng HH:mm-HH:mm");
                continue;
            }

            // Duyệt các cột ngày (col 1 = T2, col 7 = CN hoặc map theo ngày)
            for (int col = 1; col < header.size() && col < row.size(); col++) {
                HeaderInfo info = colInfos[col];
                if (info == null) continue;

                String cell = getString(row, col).trim();
                if (cell.isBlank()) continue;

                try {
                    parseCellAndSave(cell, startTime, endTime, info.dayOfWeek(), info.date(), user);
                    successCount++;
                } catch (Exception e) {
                    errors.add("Hàng " + (i + 1) + " cột " + getString(header, col) + ": " + e.getMessage());
                    log.warn("Grid parse error row={} col={}: {}", i + 1, col, e.getMessage());
                }
            }
        }
        return successCount;
    }

    /**
     * Parse nội dung 1 ô trong grid format:
     * "Tên môn|Mã môn|Phòng|Giảng viên"
     * Chỉ tên môn là bắt buộc; các trường còn lại tùy chọn.
     */
    private void parseCellAndSave(String cell, String startTime, String endTime,
                                   int dayOfWeek, LocalDate date, User user) {
        String[] parts = cell.split("\\|");
        String name    = parts.length > 0 ? parts[0].trim() : "";
        String code    = parts.length > 1 ? parts[1].trim() : null;
        String room    = parts.length > 2 ? parts[2].trim() : null;
        String teacher = parts.length > 3 ? parts[3].trim() : null;

        if (name.isBlank()) throw new IllegalArgumentException("Tên môn không được để trống");

        Subject subject = Subject.builder()
                .user(user)
                .name(name)
                .code(code != null && !code.isBlank() ? code : null)
                .teacher(teacher != null && !teacher.isBlank() ? teacher : null)
                .isActive(true)
                .build();
        subject = subjectRepository.save(subject);

        ClassSession session = ClassSession.builder()
                .subject(subject)
                .dayOfWeek(dayOfWeek)
                .startTime(startTime)
                .endTime(endTime)
                .room(room != null && !room.isBlank() ? room : null)
                .weekType("ALL")
                .date(date)
                .build();
        classScheduleRepository.save(session);
    }

    /**
     * Parse format CŨ: mỗi hàng = 1 buổi học
     * [Tên môn, Mã môn, Thứ, Giờ bắt đầu, Giờ kết thúc, Phòng, Giảng viên]
     * (hàng 1 là header → bỏ qua, data từ hàng 2)
     */
    private int parseRowSheet(List<List<Object>> rows, User user, List<String> errors) {
        int successCount = 0;
        // rows[0] là header → bắt đầu từ index 1
        for (int i = 1; i < rows.size(); i++) {
            try {
                parseAndSaveRow(rows.get(i), user, i + 1);
                successCount++;
            } catch (Exception e) {
                errors.add("Hàng " + (i + 1) + ": " + e.getMessage());
                log.warn("Row parse error row={}: {}", i + 1, e.getMessage());
            }
        }
        return successCount;
    }



    // ═══════════════════════════════════════════════════════════
    //  3. Lấy lịch học (để bot hiển thị)
    // ═══════════════════════════════════════════════════════════

    /**
     * Lấy lịch học hôm nay của user từ DB (ưu tiên lịch theo ngày cụ thể, fallback lịch tuần mặc định).
     */
    public List<ScheduleItem> getTodaySchedule(Long telegramId) {
        User user = getUserByTelegramId(telegramId);
        LocalDate today = LocalDate.now();
        int javaDow = today.getDayOfWeek().getValue();

        List<ClassSession> sessions = classScheduleRepository
                .findByUserIdAndDate(user.getId(), today);
        if (sessions.isEmpty()) {
            sessions = classScheduleRepository
                    .findByUserIdAndDayOfWeekAndDateIsNull(user.getId(), javaDow);
        }
        return sessions.stream().map(ScheduleItem::from).toList();
    }

    /**
     * Lấy toàn bộ lịch học trong tuần của user từ DB (gộp lịch ngày cụ thể tuần này + lịch tuần mặc định).
     */
    public List<ScheduleItem> getWeeklySchedule(Long telegramId) {
        User user = getUserByTelegramId(telegramId);
        LocalDate today = LocalDate.now();
        LocalDate monday = today.with(java.time.DayOfWeek.MONDAY);

        List<ClassSession> weeklySessions = new java.util.ArrayList<>();
        for (int i = 0; i < 7; i++) {
            LocalDate date = monday.plusDays(i);
            int dow = i + 1;
            List<ClassSession> sessions = classScheduleRepository
                    .findByUserIdAndDate(user.getId(), date);
            if (sessions.isEmpty()) {
                sessions = classScheduleRepository
                        .findByUserIdAndDayOfWeekAndDateIsNull(user.getId(), dow);
            }
            weeklySessions.addAll(sessions);
        }
        return weeklySessions.stream().map(ScheduleItem::from).toList();
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
            // Đọc cả header để detect format
            ValueRange response = sheetsClient.spreadsheets().values()
                    .get(spreadsheetId, "A1:ZZ")
                    .execute();

            List<List<Object>> rows = response.getValues();
            if (rows == null || rows.isEmpty()) {
                return SyncResult.error("Sheet trống hoặc chưa có dữ liệu.");
            }

            // Auto-detect format
            List<Object> header = rows.get(0);
            boolean isGrid = isDailyGridFormat(header);
            log.info("User {} daily sync – format: {}", telegramId,
                     isGrid ? "GRID (Thời gian | T2..CN)" : "ROW (Thứ|Giờ|Hoạt động)");

            // Xóa lịch cũ
            dailyActivityRepository.deleteAllByUser(user);
            dailyActivityRepository.flush();

            List<String> errors = new ArrayList<>();
            int successCount;

            if (isGrid) {
                successCount = parseDailyGridSheet(rows, user, errors);
            } else {
                // Format cũ: từ hàng 2 (bỏ header)
                successCount = 0;
                for (int i = 1; i < rows.size(); i++) {
                    List<Object> row = rows.get(i);
                    if (row.isEmpty()) continue;
                    String first = row.get(0) != null ? row.get(0).toString().trim() : "";
                    if (first.startsWith("#") || first.isBlank()) continue;
                    try {
                        parseDailyRow(row, user, i);
                        successCount++;
                    } catch (Exception e) {
                        errors.add("Hàng " + (i + 1) + ": " + e.getMessage());
                        log.warn("Lỗi parse hàng {} daily: {}", i + 1, e.getMessage());
                    }
                }
            }

            settings.setSheetSyncedAt(LocalDateTime.now());
            userSettingsRepository.save(settings);
            log.info("✅ Sync daily schedule xong user {} – {} hoạt động, {} lỗi",
                     telegramId, successCount, errors.size());
            return SyncResult.success(successCount, errors);

        } catch (IllegalArgumentException e) {
            log.warn("Lỗi cấu hình dữ liệu khi sync daily sheet của user {}: {}", telegramId, e.getMessage());
            return SyncResult.error("❌ " + e.getMessage());
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
     * Nhận diện format lịch sinh hoạt dạng lưới.
     * Header[0] = "Thời gian" / "Giờ" / "Ca"
     * Header[1] = "Thứ 2" / "T2" / "2" hoặc ngày dd/MM/yyyy
     */
    private boolean isDailyGridFormat(List<Object> header) {
        if (header == null || header.size() < 2) return false;
        String col0 = header.get(0).toString().trim().toLowerCase();
        boolean col0ok = col0.contains("thời gian") || col0.contains("giờ") || col0.contains("ca");
        boolean col1ok = parseHeader(header.get(1).toString()) != null;
        return col0ok && col1ok;
    }

    /**
     * Parse lịch sinh hoạt format lưới (GRID):
     *   Hàng 1 (header): Thời gian | Thứ 2 | Thứ 3 | Thứ 4 | Thứ 5 | Thứ 6 | Thứ 7 | CN (hoặc ngày tháng)
     *   Hàng 2+:         07:00-09:30 | Giải tích 1 | ... | (trống nếu không có HĐ)
     *
     * Quy tắc:
     *  - Mỗi ô = tên hoạt động (free-text), trống = không có gì
     *  - Cột map theo thứ hoặc ngày
     *  - Nếu tất cả các ô trong 1 hàng giống nhau → lưu 1 record dayOfWeek=null (mọi ngày)
     */
    private int parseDailyGridSheet(List<List<Object>> rows, User user, List<String> errors) {
        List<Object> header = rows.get(0);
        HeaderInfo[] colInfos = new HeaderInfo[header.size()];
        java.util.Set<LocalDate> dateSet = new java.util.HashSet<>();
        for (int col = 1; col < header.size(); col++) {
            HeaderInfo info = parseHeader(getString(header, col));
            if (info != null) {
                if (info.date() != null) {
                    if (dateSet.contains(info.date())) {
                        throw new IllegalArgumentException("Trùng lặp ngày " + getString(header, col) + " ở các cột khác nhau. Vui lòng kiểm tra lại sheet!");
                    }
                    dateSet.add(info.date());
                }
                colInfos[col] = info;
            }
        }

        int successCount = 0;
        int sortOrder    = 0;

        for (int i = 1; i < rows.size(); i++) {   // bỏ header
            List<Object> row = rows.get(i);
            if (row == null || row.isEmpty()) continue;

            String timeSlot = getString(row, 0).trim();
            if (timeSlot.isBlank()) continue;

            // Parse giờ: "07:00-09:30" hoặc "07:00–09:30"
            String startTime, endTime;
            try {
                String[] t = timeSlot.split("[-–]", 2);
                startTime = t[0].trim();
                endTime   = t[1].trim();
            } catch (Exception ex) {
                errors.add("Hàng " + (i + 1) + ": Giờ '" + timeSlot + "' không đúng định dạng HH:mm-HH:mm");
                continue;
            }

            // Thu thập hoạt động cho từng ngày trong tuần
            String[] activities = new String[7]; // index 0=T2, 6=CN
            java.util.Arrays.fill(activities, "");
            for (int col = 1; col < header.size() && col < row.size(); col++) {
                HeaderInfo info = colInfos[col];
                if (info == null) continue;
                String cell = getString(row, col).trim();
                if (cell.isBlank()) continue;

                if (info.date() != null) {
                    // Nếu là ngày cụ thể → lưu luôn hoạt động riêng ngày đó
                    try {
                        saveDailyActivity(user, info.dayOfWeek(), info.date(), startTime, endTime, cell, sortOrder++);
                        successCount++;
                    } catch (Exception ex) {
                        errors.add("Hàng " + (i + 1) + " ngày " + getString(header, col) + ": " + ex.getMessage());
                    }
                } else {
                    // Nếu là thứ thông thường -> gán vào activities mảng để kiểm tra allSame
                    activities[info.dayOfWeek() - 1] = cell;
                }
            }

            // Lưu riêng các thứ lặp lại hàng tuần (nếu có gom cụm)
            boolean hasWeeklyActivities = false;
            for (String act : activities) {
                if (!act.isBlank()) { hasWeeklyActivities = true; break; }
            }
            if (hasWeeklyActivities) {
                boolean allSame = true;
                String firstNonEmpty = null;
                for (String act : activities) {
                    if (!act.isBlank()) {
                        if (firstNonEmpty == null) firstNonEmpty = act;
                        else if (!act.equals(firstNonEmpty)) { allSame = false; break; }
                    } else {
                        allSame = false; break;
                    }
                }

                if (allSame && firstNonEmpty != null) {
                    try {
                        saveDailyActivity(user, null, null, startTime, endTime, firstNonEmpty, sortOrder++);
                        successCount++;
                    } catch (Exception ex) {
                        errors.add("Hàng " + (i + 1) + ": " + ex.getMessage());
                    }
                } else {
                    for (int d = 0; d < 7; d++) {
                        if (activities[d].isBlank()) continue;
                        try {
                            saveDailyActivity(user, d + 1, null, startTime, endTime, activities[d], sortOrder++);
                            successCount++;
                        } catch (Exception ex) {
                            errors.add("Hàng " + (i + 1) + " T" + (d + 2) + ": " + ex.getMessage());
                        }
                    }
                }
            }
        }
        return successCount;
    }

    /** Lưu 1 DailyActivity vào DB. dayOfWeek=null nghĩa là mọi ngày. */
    private void saveDailyActivity(User user, Integer dayOfWeek, LocalDate date,
                                    String startTime, String endTime,
                                    String activity, int sortOrder) {
        // Phân loại category tự động từ tên hoạt động
        String cat = autoCategory(activity);
        DailyActivity da = DailyActivity.builder()
                .user(user)
                .dayOfWeek(dayOfWeek)
                .date(date)
                .startTime(startTime)
                .endTime(endTime)
                .activity(activity)
                .category(cat)
                .note(null)
                .sortOrder(sortOrder)
                .build();
        dailyActivityRepository.save(da);
    }

    /** Phân loại tự động dựa vào tên hoạt động. */
    private String autoCategory(String activity) {
        String a = activity.toLowerCase();
        if (a.contains("ngủ"))                                          return "Nghỉ ngơi";
        if (a.contains("ăn") || a.contains("bữa"))                     return "Sinh hoạt";
        if (a.contains("vệ sinh") || a.contains("tắm"))                 return "Sinh hoạt";
        if (a.contains("thể dục") || a.contains("thể thao")
                || a.contains("tập"))                                   return "Sức khỏe";
        if (a.contains("học") || a.contains("tự học")
                || a.contains("bài tập") || a.contains("ôn"))          return "Học tập";
        if (a.contains("giải trí") || a.contains("nghỉ"))              return "Giải trí";
        return "Khác";
    }

    /**
     * Lấy lịch sinh hoạt của 1 ngày cụ thể (kết hợp "Tất cả" + ngày đó).
     */
    public List<DailyActivityItem> getDailyActivities(Long telegramId, LocalDate date) {
        User user = getUserByTelegramId(telegramId);
        int dayOfWeek = date.getDayOfWeek().getValue();

        List<DailyActivity> activities = dailyActivityRepository
                .findByUserIdAndDate(user.getId(), date);
        if (activities.isEmpty()) {
            activities = dailyActivityRepository
                    .findByUserIdAndDayOfWeekAndDateIsNull(user.getId(), dayOfWeek);
        }
        return activities.stream().map(DailyActivityItem::from).toList();
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

    // ═══════════════════════════════════════════════════════════
    //  GRID FORMAT PARSER – Lưới thời khóa biểu
    //  Hàng 1 = Header: "Giờ bắt đầu - Giờ kết thúc | Thứ 2 | Thứ 3 | ..."
    //  Hàng 2+ = Data:  "07:30 - 09:30 | Giải tích 1 | Vật lý | ..."
    // ═══════════════════════════════════════════════════════════

    /**
     * Kiểm tra xem sheet có phải format lưới không.
     * Nhận biết bằng cột đầu tiên của header chứa " - " (dạng "HH:MM - HH:MM").
     */
    private boolean isGridFormatRows(List<List<Object>> allRows) {
        if (allRows == null || allRows.isEmpty()) return false;
        List<Object> header = allRows.get(0);
        if (header.isEmpty()) return false;
        String first = header.get(0).toString().toLowerCase().trim();
        // Grid format: cột A header chứa "giờ" hoặc "-" hoặc "bắt đầu"
        return first.contains("giờ") || first.contains("bắt đầu") || first.contains(" - ");
    }

    /**
     * Đọc header của sheet grid để lấy mapping: index cột → dayOfWeek.
     *
     * Header ví dụ: ["Giờ bắt đầu - Giờ kết thúc", "Thứ 2", "Thứ 3", "Thứ 4", "Thứ 5", "Thứ 6", "Thứ 7", "Chủ nhật"]
     * Kết quả: { 1 → 1(T2), 2 → 2(T3), 3 → 3(T4), 4 → 4(T5), 5 → 5(T6), 6 → 6(T7), 7 → 7(CN) }
     */
    private java.util.Map<Integer, Integer> parseGridHeader(List<Object> header) {
        java.util.Map<Integer, Integer> colToDow = new java.util.LinkedHashMap<>();
        for (int c = 1; c < header.size(); c++) {
            String cell = header.get(c).toString().toLowerCase().trim()
                    .replace("thứ", "").replace("thu", "")
                    .replace(" ", "").replace("_", "");
            Integer dow = switch (cell) {
                case "2", "hai", "t2", "monday",    "mon"      -> 1;
                case "3", "ba",  "t3", "tuesday",   "tue"      -> 2;
                case "4", "tu",  "t4", "wednesday", "wed"      -> 3;
                case "5", "nam", "t5", "thursday"              -> 4;
                case "6", "sau", "t6", "friday",    "fri"      -> 5;
                case "7", "bay", "t7", "saturday",  "sat"      -> 6;
                case "8", "cn",       "sunday",     "sun",
                     "chunhat", "chủnhật"                      -> 7;
                default -> null;
            };
            if (dow != null) colToDow.put(c, dow);
        }
        return colToDow;
    }

    /**
     * Parse 1 ô thời gian dạng "07:30 - 09:30" → [startTime, endTime].
     * Hỗ trợ cả dạng "07:30-09:30" và "07:30 – 09:30".
     */
    private String[] parseTimeSlot(String raw) {
        if (raw == null || raw.isBlank()) return null;
        // Normalize dashes
        String normalized = raw.replace("–", "-").replace("—", "-").trim();
        String[] parts = normalized.split("-", 2);
        if (parts.length < 2) return null;
        String start = parts[0].trim();
        String end   = parts[1].trim();
        if (start.isBlank() || end.isBlank()) return null;
        return new String[]{ start, end };
    }

    /**
     * Sync sheet dạng lưới vào daily_activities.
     * Đọc từ range A1:Z (lấy cả header ở hàng 1).
     */
    @Transactional
    public SyncResult syncGridScheduleFromSheet(Long telegramId) {
        if (sheetsClient == null) {
            return SyncResult.error("Google Sheets API chưa được cấu hình trên server.");
        }

        User user = getUserByTelegramId(telegramId);
        UserSettings settings = getUserSettings(user);
        String sheetUrl = settings.getGoogleSheetUrl();
        if (sheetUrl == null || sheetUrl.isBlank()) {
            return SyncResult.error("Bạn chưa liên kết Google Sheet!\nDùng: /setsheet <link>");
        }

        String spreadsheetId = extractSpreadsheetId(sheetUrl);
        if (spreadsheetId == null) {
            return SyncResult.error("Link sheet không hợp lệ.");
        }

        try {
            // Đọc cả hàng header (A1:Z)
            ValueRange response = sheetsClient.spreadsheets().values()
                    .get(spreadsheetId, "A1:Z")
                    .execute();

            List<List<Object>> rows = response.getValues();
            if (rows == null || rows.size() < 2) {
                return SyncResult.error("Sheet cần ít nhất 2 hàng (header + dữ liệu).");
            }

            // Parse header → mapping cột → thứ
            List<Object> header = rows.get(0);
            java.util.Map<Integer, Integer> colToDow = parseGridHeader(header);

            if (colToDow.isEmpty()) {
                return SyncResult.error(
                    "Không đọc được tên ngày từ header.\n" +
                    "Hàng 1 cần có: Thứ 2, Thứ 3, Thứ 4, Thứ 5, Thứ 6 (hoặc T2–CN)");
            }

            // Xóa lịch cũ
            dailyActivityRepository.deleteAllByUser(user);
            dailyActivityRepository.flush();

            List<String> errors = new ArrayList<>();
            int successCount = 0;
            int sortOrder = 0;

            // Đọc từ hàng 2 trở đi (bỏ header)
            for (int r = 1; r < rows.size(); r++) {
                List<Object> row = rows.get(r);
                if (row.isEmpty()) continue;

                String timeCell = getString(row, 0);
                if (timeCell.startsWith("#") || timeCell.isBlank()) continue;

                String[] times = parseTimeSlot(timeCell);
                if (times == null) {
                    errors.add("Hàng " + (r + 1) + ": Định dạng giờ không hợp lệ '" + timeCell + "'");
                    continue;
                }

                String startTime = times[0];
                String endTime   = times[1];

                // Duyệt từng cột ngày
                for (java.util.Map.Entry<Integer, Integer> entry : colToDow.entrySet()) {
                    int col = entry.getKey();
                    int dow = entry.getValue();

                    if (col >= row.size()) continue;
                    String activityText = getString(row, col);
                    if (activityText.isBlank()) continue;  // Ô trống = không có hoạt động

                    // Parse "Tên hoạt động (Ghi chú)" → tách note trong ngoặc
                    String activity = activityText;
                    String note     = null;
                    int paren = activityText.lastIndexOf('(');
                    if (paren > 0 && activityText.endsWith(")")) {
                        activity = activityText.substring(0, paren).trim();
                        note     = activityText.substring(paren + 1, activityText.length() - 1).trim();
                    }

                    String category = inferCategory(activity);

                    DailyActivity da = DailyActivity.builder()
                            .user(user)
                            .dayOfWeek(dow)
                            .startTime(startTime)
                            .endTime(endTime)
                            .activity(activity)
                            .category(category)
                            .note(note)
                            .sortOrder(sortOrder++)
                            .build();
                    dailyActivityRepository.save(da);
                    successCount++;
                }
            }

            settings.setSheetSyncedAt(LocalDateTime.now());
            userSettingsRepository.save(settings);

            log.info("✅ Sync grid schedule xong user {} – {} slots", telegramId, successCount);
            return SyncResult.success(successCount, errors);

        } catch (java.io.IOException e) {
            log.error("Lỗi đọc sheet grid {}: {}", telegramId, e.getMessage());
            if (e.getMessage() != null && e.getMessage().contains("403")) {
                return SyncResult.error("❌ Không có quyền đọc sheet!\nShare → Anyone with link → Viewer");
            }
            return SyncResult.error("❌ Lỗi kết nối: " + e.getMessage());
        }
    }

    /**
     * Auto-detect format sheet rồi sync đúng parser.
     * - Nếu header có "Thứ 2/3/4..." → grid format
     * - Ngược lại → row format (6 cột cũ)
     */
    @Transactional
    public SyncResult autoSyncSheet(Long telegramId) {
        if (sheetsClient == null) {
            return SyncResult.error("Google Sheets API chưa được cấu hình trên server.");
        }

        User user = getUserByTelegramId(telegramId);
        UserSettings settings = getUserSettings(user);
        String sheetUrl = settings.getGoogleSheetUrl();
        if (sheetUrl == null || sheetUrl.isBlank()) {
            return SyncResult.error("Bạn chưa liên kết Google Sheet!\nDùng: /setsheet <link>");
        }

        String spreadsheetId = extractSpreadsheetId(sheetUrl);
        try {
            // Đọc hàng đầu để detect format
            ValueRange probe = sheetsClient.spreadsheets().values()
                    .get(spreadsheetId, "A1:Z1")
                    .execute();

            List<List<Object>> headerRows = probe.getValues();
            boolean isGrid = isGridFormatRows(headerRows);

            log.info("User {} sheet format detected: {}", telegramId, isGrid ? "GRID" : "ROW");

            if (isGrid) {
                return syncGridScheduleFromSheet(telegramId);
            } else {
                return syncDailyScheduleFromSheet(telegramId);
            }

        } catch (java.io.IOException e) {
            return SyncResult.error("❌ Lỗi kết nối Google Sheets: " + e.getMessage());
        }
    }

    /**
     * Tự động suy luận danh mục từ tên hoạt động.
     */
    private String inferCategory(String activity) {
        if (activity == null || activity.isBlank()) return "Khác";
        String s = activity.toLowerCase();
        if (s.contains("ngủ") || s.contains("nghỉ") || s.contains("nướng"))         return "Nghỉ ngơi";
        if (s.contains("vệ sinh") || s.contains("dọn") || s.contains("giặt")
                || s.contains("chuẩn bị") || s.contains("dậy"))                     return "Sinh hoạt";
        if (s.contains("ăn") || s.contains("brunch") || s.contains("canteen"))       return "Ăn uống";
        if (s.contains("học") || s.contains("thi") || s.contains("bài")
                || s.contains("ôn") || s.contains("đồ án") || s.contains("lab")
                || s.contains("tiếng anh") || s.contains("giải tích")
                || s.contains("vật lý") || s.contains("triết") || s.contains("lập trình")
                || s.contains("cơ sở") || s.contains("thư viện"))                   return "Học tập";
        if (s.contains("thể dục") || s.contains("tập") || s.contains("gym")
                || s.contains("chạy") || s.contains("bóng") || s.contains("sport")) return "Thể dục";
        if (s.contains("giải trí") || s.contains("youtube") || s.contains("phim")
                || s.contains("nhạc") || s.contains("chơi") || s.contains("đọc")
                || s.contains("gọi điện") || s.contains("mua sắm"))                  return "Giải trí";
        if (s.contains("di chuyển") || s.contains("xe") || s.contains("đến trường")
                || s.contains("về nhà") || s.contains("bus"))                        return "Di chuyển";
        return "Khác";
    }
}
