# Activity Diagram — HUSTStudy Bot

## Tổng quan

Sơ đồ hoạt động mô tả luồng xử lý của các chức năng chính, phân chia trách nhiệm giữa **Người dùng**, **Python Bot**, và **Java API + MySQL**.

Tên bảng/cột dùng đúng theo SQL thực tế (`V1__init_schema.sql`).

---

## Activity 1 — Ghi chi tiêu (/addexpense)

### Luồng chính
1. User gõ `/addexpense <số_tiền> <ghi_chú>`.
2. Bot parse tham số. Sai format → báo lỗi.
3. Bot hiển thị keyboard inline chọn danh mục (từ `expense_categories`).
4. Sau khi chọn, bot gọi `POST /api/expenses`.
5. API INSERT vào bảng `expenses`, tính `SUM(amount)` tháng hiện tại.
6. Kiểm tra `budgets.amount` và `warn_threshold` (default 0.80).
7. Nếu vượt ngưỡng và chưa gửi cảnh báo (`is_notified_80 = 0`) → gửi cảnh báo + cập nhật cờ.

```plantuml
@startuml activity_addexpense
title Activity Diagram — Ghi chi tiêu (/addexpense)

skinparam ActivityBackgroundColor LightYellow
skinparam ActivityBorderColor DarkOrange
skinparam ActivityArrowColor DarkOrange
skinparam swimlane {
    BorderColor DarkGray
    TitleFontSize 13
}

|Người dùng|
start
:Gõ /addexpense 35000 cơm trưa;

|Python Bot|
:Nhận lệnh từ Telegram;
:Parse: amount=35000, note="cơm trưa";

if (Parse được số tiền hợp lệ?) then (Có)
    :Lưu {amount, note} vào context.user_data;
    :Gọi GET /api/expense-categories\nđể lấy danh mục;
    :Gửi InlineKeyboardMarkup\n[🍜 Ăn uống] [🚌 Di chuyển]\n[📚 Học phí & Sách] [🎮 Giải trí] ...;

    |Người dùng|
    :Chọn danh mục (vd: "🍜 Ăn uống");

    |Python Bot|
    :Nhận CallbackQuery { data: "cat_1" };
    :Đọc {amount, note} từ context.user_data;
    :Gọi POST /api/expenses\n{ telegramId, categoryId:1, type:"EXPENSE",\n  amount:35000, note:"cơm trưa" };

    |Java API + MySQL|
    :INSERT INTO expenses\n(user_id, category_id, type,\namount, note, transaction_at);
    :SELECT SUM(amount) FROM expenses\nWHERE user_id=? AND category_id=?\nAND type='EXPENSE'\nAND MONTH(transaction_at)=MONTH(NOW());
    :SELECT amount, warn_threshold, is_notified_80\nFROM budgets\nWHERE user_id=? AND category_id=?\nAND month=? AND year=?;
    :Tính spentPct = spent / budget_amount;

    if (budget tồn tại?) then (Có)
        if (spentPct >= warn_threshold\nAND is_notified_80 = 0?) then (Có)
            :UPDATE budgets SET is_notified_80=1;
            :Trả về warned=true, spentPct;
        else (Không)
            :Trả về warned=false, spentPct;
        endif
    else (Không)
        :Trả về warned=false, spentPct=null;
    endif
    :HTTP 201 { expenseId, spentPct, warned };

    |Python Bot|
    if (warned = true?) then (Có)
        :Gửi:\n"✅ Đã ghi: -35,000đ | 🍜 Ăn uống | cơm trưa\n⚠️ Đã dùng {spentPct}% ngân sách tháng này!";
    else (Không)
        :Gửi:\n"✅ Đã ghi: -35,000đ | 🍜 Ăn uống | cơm trưa";
    endif

else (Không)
    :Gửi:\n"❌ Sai format!\nDùng: /addexpense <số_tiền> <ghi_chú>\nVD: /addexpense 35000 cơm trưa";
endif

|Người dùng|
:Nhận phản hồi;
stop
@enduml
```

### Điểm quyết định

| Điều kiện | True | False |
|---|---|---|
| Parse được số tiền? | Hiển thị keyboard danh mục | Gửi hướng dẫn lỗi |
| Ngân sách tồn tại? | Tính và kiểm tra threshold | Không cảnh báo |
| spentPct ≥ warn_threshold AND is_notified_80=0? | Cảnh báo + đánh dấu | Xác nhận thông thường |

---

## Activity 2 — Ôn tập từ vựng (/quiz)

### Luồng chính
1. User gõ `/quiz`.
2. Bot gọi API lấy từ cần ôn: `next_review_at <= NOW()` từ bảng `vocabularies`.
3. Nếu không có từ → thông báo hoàn thành.
4. Shuffle danh sách → vòng lặp quiz từng từ.
5. Mỗi câu: bot hỏi → user trả lời → kiểm tra (case-insensitive).
6. Kết thúc: INSERT `vocab_sessions`, INSERT nhiều `vocab_answers`, cập nhật `vocabularies` theo SM-2.

```plantuml
@startuml activity_quiz
title Activity Diagram — Ôn tập từ vựng (/quiz)

skinparam ActivityBackgroundColor LightCyan
skinparam ActivityBorderColor DarkBlue
skinparam ActivityArrowColor DarkBlue
skinparam swimlane {
    BorderColor DarkGray
}

|Người dùng|
start
:Gõ /quiz;

|Python Bot|
:Gọi GET /api/vocabularies\n?userId={telegramId}&dueOnly=true;

|Java API + MySQL|
:SELECT id, word, meaning, pronunciation\nFROM vocabularies\nWHERE user_id=?\nAND (next_review_at IS NULL\n  OR next_review_at <= NOW())\nORDER BY next_review_at ASC\nLIMIT 20;
:Trả danh sách từ cần ôn;

|Python Bot|
if (Có từ cần ôn?) then (Có)
    :Shuffle danh sách từ;
    :Khởi tạo session trong memory:\ncorrect=0, wrong=0, answers=[];

    repeat
        :Lấy từ tiếp theo;
        :Gửi câu hỏi:\n"📖 *{word}*\nNghĩa là gì?\n(Câu {n}/{total})";

        |Người dùng|
        :Gõ đáp án;

        |Python Bot|
        :So sánh đáp án (strip + lowercase)\nvới meaning;

        if (Đúng?) then (Đúng)
            :correct += 1;
            :answers.append({vocab_id, is_correct:true, response_time});
            :Gửi: "✅ Chính xác!\n💡 VD: {example}";
        else (Sai)
            :wrong += 1;
            :answers.append({vocab_id, is_correct:false, response_time});
            :Gửi: "❌ Sai!\n📌 Đáp án: {meaning}\n💡 VD: {example}";
        endif

    repeat while (Còn từ tiếp theo?) is (Có)
    -> Hết từ;

    :scorePercent = correct * 100 / total;
    :Gọi POST /api/vocab-sessions\n{ telegramId, totalQuestions, correctCount,\n  wrongCount, answers:[{vocabId, isCorrect, responseTime}] };

    |Java API + MySQL|
    :INSERT INTO vocab_sessions\n(user_id, started_at, ended_at,\ntotal_questions, correct_count,\nwrong_count, status='DONE');
    :INSERT INTO vocab_answers (session_id,\nvocab_id, user_answer,\nis_correct, response_time)\nFOR EACH câu trả lời;
    :Cập nhật vocabularies theo SM-2:\n- Đúng: review_interval *= ease_factor\n- Sai: review_interval = 1\nnext_review_at = NOW() + review_interval ngày;
    :HTTP 201 { sessionId, scorePercent };

    |Python Bot|
    :Gửi tổng kết:\n"🏆 Kết quả quiz:\n✅ Đúng: {correct}/{total}\n📊 Điểm: {scorePercent}%";

else (Không)
    :Gửi:\n"🎉 Tuyệt vời! Không có từ nào\ncần ôn hôm nay.\nHãy thêm từ mới bằng /addword";
endif

|Người dùng|
:Nhận kết quả;
stop
@enduml
```

### Thuật toán SM-2 (Spaced Repetition)

| Trả lời | `review_interval` mới | `ease_factor` mới | `next_review_at` |
|---|---|---|---|
| Đúng | `interval × ease_factor` (làm tròn) | `ease_factor + 0.1` (tối đa 2.50) | `NOW() + interval ngày` |
| Sai | 1 ngày | `ease_factor - 0.2` (tối thiểu 1.30) | `NOW() + 1 ngày` |

- `ease_factor` khởi tạo: **2.50** (dễ), giảm dần khi hay sai.
- `review_interval` khởi tạo: **1 ngày**.
- Từ trả lời đúng liên tục → chu kỳ tăng: 1 → 2 → 5 → 12 → 30 ngày...
