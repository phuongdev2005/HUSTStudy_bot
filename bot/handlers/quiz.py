# ============================================================
#  Handler – Ôn tập từ vựng (Quiz)
#  /quiz     — Bắt đầu ôn 1 từ ngẫu nhiên (spaced repetition)
#  /addword  — Thêm từ: /addword apple - quả táo
#  /words    — Xem danh sách từ của mình
#
#  Flow quiz: Bot hỏi nghĩa → User trả lời → Bot chấm → Cập nhật level
# ============================================================

import logging
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes, ConversationHandler

from services.api_client import api
from handlers.menu import MAIN_KEYBOARD

logger = logging.getLogger(__name__)

# ConversationHandler states
QUIZ_WAITING_ANSWER = "quiz_answer"


async def quiz_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """/quiz — Lấy 1 từ cần ôn và hỏi user."""
    tid = update.effective_user.id
    try:
        word = await api.get_next_quiz_word(tid)
        if not word:
            kb = InlineKeyboardMarkup([[
                InlineKeyboardButton("➕ Thêm từ vựng", callback_data="quiz_add_hint"),
            ]])
            await update.message.reply_text(
                "📚 *Ôn tập từ vựng*\n\n"
                "Bạn chưa có từ nào trong danh sách!\n"
                "Thêm từ bằng lệnh:\n"
                "`/addword <từ tiếng Anh> - <nghĩa tiếng Việt>`\n\n"
                "Ví dụ: `/addword computer - máy tính`",
                parse_mode="Markdown",
                reply_markup=kb,
            )
            return

        # Lưu từ đang quiz vào context
        context.user_data["quiz_word"] = word

        word_id     = word.get("id")
        word_text   = word.get("word", "?")
        level       = word.get("level", 0)
        example     = word.get("example") or ""
        pron        = word.get("pronunciation") or ""

        level_bar = "⭐" * min(level, 5) + "☆" * (5 - min(level, 5))
        example_line = f"\n\n💬 _{example}_" if example else ""
        pron_line    = f"\n🔊 {pron}" if pron else ""

        kb = InlineKeyboardMarkup([
            [
                InlineKeyboardButton("✅ Biết rồi",     callback_data=f"quiz_know_{word_id}"),
                InlineKeyboardButton("❌ Chưa biết",    callback_data=f"quiz_dontknow_{word_id}"),
            ],
            [
                InlineKeyboardButton("👁 Xem đáp án",   callback_data=f"quiz_reveal_{word_id}"),
                InlineKeyboardButton("⏭ Bỏ qua",        callback_data=f"quiz_skip_{word_id}"),
            ],
        ])

        await update.message.reply_text(
            f"🧠 *Ôn từ vựng*\n\n"
            f"Từ: *{word_text}*{pron_line}\n"
            f"Level: {level_bar}{example_line}\n\n"
            f"Nghĩa của từ này là gì?\n"
            f"_(Gõ câu trả lời hoặc bấm nút bên dưới)_",
            parse_mode="Markdown",
            reply_markup=kb,
        )

    except Exception as e:
        logger.error("quiz_handler: %s", e)
        await update.message.reply_text(
            "❌ Lỗi tải từ vựng.\n\nDùng /start để đăng ký trước.",
            reply_markup=MAIN_KEYBOARD,
        )


async def addword_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """/addword <từ> - <nghĩa> [- <ví dụ>]
    Ví dụ:
      /addword computer - máy tính
      /addword computer - máy tính - I use a computer every day.
    """
    tid  = update.effective_user.id
    text = update.message.text.replace("/addword", "").strip()

    if not text or "-" not in text:
        await update.message.reply_text(
            "📖 *Thêm từ vựng*\n\n"
            "Cú pháp:\n"
            "`/addword <từ tiếng Anh> - <nghĩa tiếng Việt>`\n\n"
            "Ví dụ:\n"
            "• `/addword computer - máy tính`\n"
            "• `/addword algorithm - thuật toán - An algorithm solves a problem`",
            parse_mode="Markdown",
        )
        return

    parts   = text.split("-", 2)
    word    = parts[0].strip()
    meaning = parts[1].strip() if len(parts) > 1 else ""
    example = parts[2].strip() if len(parts) > 2 else None

    if not word or not meaning:
        await update.message.reply_text("❌ Từ và nghĩa không được để trống.")
        return

    try:
        await api.add_word(tid, word, meaning, example)
        await update.message.reply_text(
            f"✅ *Đã thêm từ mới!*\n\n"
            f"📖 *{word}*\n"
            f"🔤 {meaning}"
            + (f"\n💬 _{example}_" if example else "")
            + "\n\n🧠 Dùng /quiz để ôn tập!",
            parse_mode="Markdown",
        )
    except Exception as e:
        logger.error("addword_handler: %s", e)
        await update.message.reply_text(f"❌ Lỗi thêm từ: {e}")


async def words_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """/words — Xem danh sách từ vựng của bạn."""
    tid = update.effective_user.id
    try:
        words = await api.get_all_words(tid)
        if not words:
            await update.message.reply_text(
                "📚 Chưa có từ vựng nào.\n"
                "Thêm bằng: `/addword apple - quả táo`",
                parse_mode="Markdown",
            )
            return

        total = len(words)
        lines = [f"📚 *Từ vựng của bạn ({total} từ)*\n"]
        for w in words[:20]:   # Hiện tối đa 20
            level = w.get("level", 0)
            stars = "⭐" * min(level, 5)
            lines.append(f"• *{w.get('word')}* — {w.get('meaning')} {stars}")

        if total > 20:
            lines.append(f"\n_... và {total - 20} từ nữa_")
        lines.append(f"\n🧠 Dùng /quiz để ôn tập!")

        await update.message.reply_text("\n".join(lines), parse_mode="Markdown")
    except Exception as e:
        await update.message.reply_text(f"❌ Lỗi: {e}")


async def quiz_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Xử lý nút ✅ Biết / ❌ Chưa biết / 👁 Xem / ⏭ Bỏ qua."""
    query = update.callback_query
    await query.answer()

    tid  = query.from_user.id
    data = query.data  # quiz_know_123 / quiz_dontknow_123 / quiz_reveal_123 / quiz_skip_123

    parts    = data.split("_", 2)
    action   = parts[1] if len(parts) > 1 else ""
    word_id  = int(parts[2]) if len(parts) > 2 else 0

    word = context.user_data.get("quiz_word", {})
    meaning = word.get("meaning", "?")
    word_text = word.get("word", "?")

    if action == "reveal":
        await query.edit_message_text(
            f"👁 *{word_text}*\n\n"
            f"📖 Nghĩa: *{meaning}*\n\n"
            f"Bạn có nhớ không?",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("✅ Có, tôi biết",  callback_data=f"quiz_know_{word_id}"),
                InlineKeyboardButton("❌ Không, quên rồi", callback_data=f"quiz_dontknow_{word_id}"),
            ]]),
        )

    elif action == "know":
        try:
            await api.submit_quiz_result(tid, word_id, correct=True)
        except Exception:
            pass
        await query.edit_message_text(
            f"✅ Chính xác! *{word_text}* = {meaning}\n\n"
            f"Level tăng rồi! 📈\n"
            f"Dùng /quiz để ôn tiếp 🧠",
            parse_mode="Markdown",
        )

    elif action == "dontknow":
        try:
            await api.submit_quiz_result(tid, word_id, correct=False)
        except Exception:
            pass
        await query.edit_message_text(
            f"❌ *{word_text}* = *{meaning}*\n\n"
            f"Ghi nhớ nhé! Bot sẽ hỏi lại sớm thôi 📝\n"
            f"Dùng /quiz để ôn tiếp 🧠",
            parse_mode="Markdown",
        )

    elif action == "skip":
        await query.edit_message_text(
            f"⏭ Bỏ qua *{word_text}*\n\nDùng /quiz để ôn từ tiếp theo.",
            parse_mode="Markdown",
        )

    elif action == "add_hint":
        await query.edit_message_text(
            "📖 *Thêm từ vựng*\n\n"
            "`/addword <từ tiếng Anh> - <nghĩa tiếng Việt>`\n\n"
            "Ví dụ:\n• `/addword computer - máy tính`",
            parse_mode="Markdown",
        )
