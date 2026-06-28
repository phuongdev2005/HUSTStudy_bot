# ============================================================
#  Scheduler - Gui thong bao tu dong theo lich
# ============================================================

import logging
from datetime import datetime, date

from telegram import Bot
from telegram.ext import Application

from services.api_client import api

logger = logging.getLogger(__name__)

_sent_morning: set = set()
_hust_imported_per_user: dict = {}


def setup_scheduler(application: Application):
    """Dang ky tat ca scheduled jobs vao APScheduler cua bot."""
    scheduler = application.job_queue
    scheduler.run_repeating(morning_summary_job, interval=60, first=10)
    scheduler.run_repeating(class_remind_job, interval=300, first=30)
    scheduler.run_daily(deadline_remind_job,
                        time=datetime.strptime("08:00", "%H:%M").time())
    scheduler.run_daily(exam_remind_job,
                        time=datetime.strptime("08:05", "%H:%M").time())
    logger.info("Scheduler da khoi dong: morning/class/deadline/exam jobs")


async def morning_summary_job(context):
    global _sent_morning
    bot: Bot = context.bot
    now = datetime.now()
    today = now.date()
    current_hhmm = now.strftime("%H:%M")

    try:
        users = await api.get_all_users_with_notifications()
    except Exception as e:
        logger.warning("morning_summary_job error: %s", e)
        return

    for user in users:
        tid = user.get("telegramId")
        settings = user.get("notifications", {})
        if not settings.get("notifyDailySummary"):
            continue
        scheduled_time = settings.get("dailySummaryTime", "07:00")[:5]
        cache_key = (tid, str(today), scheduled_time)
        if cache_key in _sent_morning or current_hhmm != scheduled_time:
            continue
        _sent_morning.add(cache_key)
        try:
            await _send_morning_summary(bot, tid, settings)
        except Exception as e:
            logger.error("morning send error tid=%s: %s", tid, e)

    _sent_morning = {k for k in _sent_morning if k[1] == str(today)}


async def _send_morning_summary(bot: Bot, tid: int, settings: dict):
    import asyncio
    from handlers.hust_events import _fetch_hust_events

    now = datetime.now()
    java_dow = now.isoweekday()
    dow_names = {1: "Thu 2", 2: "Thu 3", 3: "Thu 4",
                 4: "Thu 5", 5: "Thu 6", 6: "Thu 7", 7: "CN"}
    day_name = dow_names.get(java_dow, "Hom nay")

    acts_task    = asyncio.create_task(api.get_daily_schedule(tid, java_dow))
    classes_task = asyncio.create_task(api.get_today_schedule(tid))
    hust_task    = asyncio.create_task(_fetch_hust_events())

    results = await asyncio.gather(
        acts_task, classes_task, hust_task, return_exceptions=True
    )
    activities  = results[0] if not isinstance(results[0], Exception) else []
    classes     = results[1] if not isinstance(results[1], Exception) else []
    hust_result = results[2] if not isinstance(results[2], Exception) else {}

    lines = [f"\u2600\ufe0f *Chao buoi sang! Lich {day_name}*\n"]

    if classes:
        lines.append("\ud83c\udfe5 *Lich hoc hom nay:*")
        for c in classes:
            s = (c.get("startTime") or "")[:5]
            e = (c.get("endTime")   or "")[:5]
            lines.append(f"  \ud83d\udcd6 `{s}-{e}` {c.get('subjectName','?')} - {c.get('room','?')}")
        lines.append("")

    if activities:
        lines.append("\ud83d\udccb *Lich sinh hoat noi bat:*")
        for act in activities[:4]:
            s = (act.get("startTime") or "")[:5]
            lines.append(f"  \u23f0 `{s}` {act.get('activity','?')}")
        lines.append("")

    hust_enabled  = settings.get("notifyHustEvents", True)
    upcoming_hust = hust_result.get("upcoming", []) if isinstance(hust_result, dict) else []

    if hust_enabled and upcoming_hust:
        imported   = _hust_imported_per_user.get(tid, set())
        new_events = [ev for ev in upcoming_hust if ev["id"] not in imported]

        if new_events:
            imported_titles = []
            imported_pts    = []
            for ev in new_events[:5]:
                try:
                    due_date = (ev.get("deadline") or ev["start"]).strftime("%Y-%m-%d")
                    await api.add_deadline(
                        telegram_id=tid,
                        title=ev["name"],
                        due_date=due_date,
                        subject="HUST CTSV",
                    )
                    imported.add(ev["id"])
                    imported_titles.append(ev["name"])
                    max_pts = max(
                        (c.get("CMaxPoint", 0) for c in ev.get("criteria", [])),
                        default=0
                    )
                    imported_pts.append(max_pts)
                except Exception as ex:
                    logger.warning("hust import loi ev=%s: %s", ev.get("name"), ex)

            _hust_imported_per_user[tid] = imported

            if imported_titles:
                lines.append("\ud83c\udfe8 *Su kien HUST CTSV moi:*")
                for title, pts in zip(imported_titles, imported_pts):
                    pts_str = f" \u2b50 `+{pts:.0f}d`" if pts > 0 else ""
                    lines.append(f"  \u2022 {title[:42]}{pts_str}")
                lines.append("\ud83d\udccc Da tu dong them vao Deadline!")
                lines.append("")

    if not classes and not activities:
        lines.append("Khong co lich hoc. Nghi ngoi nhe! \ud83c\udf89")

    await bot.send_message(chat_id=tid, text="\n".join(lines), parse_mode="Markdown")
    logger.info("Tom tat sang -> tid=%s", tid)


_reminded_classes: set = set()


async def class_remind_job(context):
    global _reminded_classes
    bot: Bot = context.bot
    now = datetime.now()
    today = now.date()

    try:
        users = await api.get_all_users_with_notifications()
    except Exception:
        return

    for user in users:
        tid      = user.get("telegramId")
        settings = user.get("notifications", {})
        if not settings.get("notifyClassRemind"):
            continue

        before_min = settings.get("classRemindBefore", 30)
        try:
            classes = await api.get_today_schedule(tid)
        except Exception:
            continue

        for c in classes:
            start_str = (c.get("startTime") or "")[:5]
            if not start_str:
                continue
            try:
                start_dt = datetime.combine(
                    today, datetime.strptime(start_str, "%H:%M").time()
                )
            except ValueError:
                continue

            diff_min = (start_dt - now).total_seconds() / 60
            if not (0 <= diff_min <= before_min):
                continue

            cache_key = (tid, c.get("subjectName", "?"), str(today), start_str)
            if cache_key in _reminded_classes:
                continue
            _reminded_classes.add(cache_key)

            try:
                await bot.send_message(
                    chat_id=tid,
                    text=(
                        f"\u23f0 *Nhac lich hoc!*\n\n"
                        f"\ud83d\udcd6 *{c.get('subjectName','?')}*\n"
                        f"\ud83d\udd50 Bat dau luc `{start_str}` - con ~{int(diff_min)} phut\n"
                        f"\ud83d\udccd Phong: {c.get('room','?')}"
                    ),
                    parse_mode="Markdown",
                )
            except Exception as e:
                logger.error("class_remind send error: %s", e)

    _reminded_classes = {k for k in _reminded_classes if k[2] == str(today)}


async def deadline_remind_job(context):
    bot: Bot = context.bot
    try:
        users = await api.get_all_users_with_notifications()
    except Exception:
        return

    for user in users:
        tid      = user.get("telegramId")
        settings = user.get("notifications", {})
        if not settings.get("notifyDeadline"):
            continue

        try:
            deadlines = await api.get_deadlines(tid)
        except Exception:
            continue

        urgent = []
        for dl in deadlines:
            if dl.get("isDone"):
                continue
            try:
                due  = date.fromisoformat(dl.get("dueDate", ""))
                days = (due - date.today()).days
                if 0 <= days <= 3:
                    urgent.append((days, dl))
            except Exception:
                pass

        if not urgent:
            continue

        lines = ["\u23f0 *Nhac nho: Deadline sap toi!*\n"]
        for days, dl in sorted(urgent):
            icon    = "\ud83c\udd98" if days == 0 else "\ud83d\udd34" if days == 1 else "\ud83d\udfe1"
            day_txt = "Hom nay!" if days == 0 else f"Con {days} ngay"
            lines.append(
                f"{icon} *{dl.get('title','?')}*\n"
                f"  \ud83d\udcc5 {dl.get('dueDate','?')} - _{day_txt}_"
            )

        try:
            await bot.send_message(chat_id=tid, text="\n\n".join(lines), parse_mode="Markdown")
        except Exception as e:
            logger.error("deadline_remind error tid=%s: %s", tid, e)


async def exam_remind_job(context):
    bot: Bot = context.bot
    try:
        users = await api.get_all_users_with_notifications()
    except Exception:
        return

    for user in users:
        tid      = user.get("telegramId")
        settings = user.get("notifications", {})
        if not settings.get("notifyExam"):
            continue

        remind_days = settings.get("examRemindBeforeDays", 2)
        try:
            exams = await api.get_exams(tid)
        except Exception:
            continue

        upcoming = []
        for ex in exams:
            try:
                ex_date = date.fromisoformat(ex.get("examDate", ""))
                days    = (ex_date - date.today()).days
                if 0 <= days <= remind_days:
                    upcoming.append((days, ex))
            except Exception:
                pass

        if not upcoming:
            continue

        lines = ["\ud83d\udccb *Nhac nho: Lich thi sap toi!*\n"]
        for days, ex in sorted(upcoming):
            icon    = "\ud83c\udd98" if days == 0 else "\ud83d\udd34" if days == 1 else "\ud83d\udfe1"
            day_txt = "Hom nay!" if days == 0 else f"Con {days} ngay"
            time_s  = (ex.get("startTime") or "")[:5]
            lines.append(
                f"{icon} *{ex.get('subject','?')}*\n"
                f"  \ud83d\udcc5 {ex.get('examDate','?')} \ud83d\udd50 {time_s}\n"
                f"  \ud83d\udccd {ex.get('room') or 'Chua co phong'} - _{day_txt}_"
            )

        try:
            await bot.send_message(chat_id=tid, text="\n\n".join(lines), parse_mode="Markdown")
        except Exception as e:
            logger.error("exam_remind error tid=%s: %s", tid, e)