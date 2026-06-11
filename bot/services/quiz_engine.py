# ============================================================
#  Quiz Engine – Logic hỏi đáp từ vựng & ngữ pháp
#  Quản lý phiên quiz, chấm điểm, thống kê kết quả
# ============================================================

import random
import logging

logger = logging.getLogger(__name__)

# Lưu trạng thái quiz theo telegram_id
# { telegram_id: { "words": [...], "index": 0, "correct": 0, "wrong": 0 } }
active_sessions: dict = {}


async def start_session(telegram_id: int, words: list[dict]) -> dict:
    """
    Bắt đầu phiên quiz mới.

    Args:
        telegram_id: ID người dùng Telegram
        words: Danh sách từ vựng [{"word": "apple", "meaning": "quả táo"}, ...]

    Returns:
        Câu hỏi đầu tiên
    """
    if not words:
        return {"error": "Bạn chưa có từ vựng nào. Dùng /addword để thêm!"}

    random.shuffle(words)
    active_sessions[telegram_id] = {
        "words": words,
        "index": 0,
        "correct": 0,
        "wrong": 0,
    }
    return get_next_question(telegram_id)


def get_next_question(telegram_id: int) -> dict:
    """Lấy câu hỏi tiếp theo trong phiên."""
    session = active_sessions.get(telegram_id)
    if not session:
        return {"error": "Không có phiên quiz nào đang chạy. Dùng /quiz để bắt đầu!"}

    idx = session["index"]
    if idx >= len(session["words"]):
        return get_session_result(telegram_id)

    word = session["words"][idx]["word"]
    return {
        "question": f'"{word}" nghĩa là gì?',
        "index": idx + 1,
        "total": len(session["words"]),
    }


def check_answer(telegram_id: int, user_answer: str) -> dict:
    """
    Kiểm tra đáp án của người dùng.

    Returns:
        { "correct": bool, "correct_answer": str, "next": dict }
    """
    session = active_sessions.get(telegram_id)
    if not session:
        return {"error": "Không có phiên quiz nào đang chạy."}

    idx = session["index"]
    current_word = session["words"][idx]
    correct_answer = current_word["meaning"]

    is_correct = user_answer.strip().lower() == correct_answer.strip().lower()

    if is_correct:
        session["correct"] += 1
    else:
        session["wrong"] += 1

    session["index"] += 1

    return {
        "correct": is_correct,
        "correct_answer": correct_answer,
        "next": get_next_question(telegram_id),
    }


def get_session_result(telegram_id: int) -> dict:
    """Trả về kết quả tổng kết phiên quiz."""
    session = active_sessions.pop(telegram_id, None)
    if not session:
        return {"error": "Không có phiên quiz."}

    total = session["correct"] + session["wrong"]
    score_pct = int(session["correct"] / total * 100) if total > 0 else 0

    return {
        "finished": True,
        "correct": session["correct"],
        "wrong": session["wrong"],
        "total": total,
        "score_pct": score_pct,
    }


def has_active_session(telegram_id: int) -> bool:
    """Kiểm tra user có đang trong phiên quiz không."""
    return telegram_id in active_sessions
