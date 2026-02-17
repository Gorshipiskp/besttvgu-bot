from datetime import datetime

from besttvgu_bot.api_contracts.group.models import WeekMarks
from besttvgu_bot.misc.datetime_lib import get_week_number


def get_week_mark(cur_date: datetime | None = None) -> WeekMarks:
    return WeekMarks.PLUS if (get_week_number(cur_date) - 1) % 2 == 0 else WeekMarks.MINUS


def get_week_mark_emoji(week_mark: WeekMarks) -> str:
    week_marks_emojis: dict[WeekMarks, str] = {
        WeekMarks.EVERY: "🟢",
        WeekMarks.PLUS: "🔴",
        WeekMarks.MINUS: "🔵",
    }

    return week_marks_emojis[week_mark]
