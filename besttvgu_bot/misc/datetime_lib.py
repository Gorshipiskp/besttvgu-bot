from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

import cachetools

from besttvgu_bot.consts import PAIRS_TIMES


def now() -> datetime:
    local_tz: ZoneInfo = ZoneInfo("Europe/Moscow")
    return datetime.now(local_tz)


def get_start_of_week(cur_date: datetime | None = None) -> datetime:
    date: datetime = cur_date or now()
    start_of_week: datetime = date - timedelta(days=date.weekday())

    return start_of_week.replace(hour=0, minute=0, second=0, microsecond=0)


def get_week_number(cur_date: datetime | None = None) -> int:
    date: datetime = cur_date or now()
    return get_start_of_week(date).isocalendar().week


def translate_date(date_str: str) -> str:
    months: dict[str, str] = {
        "January": "Января",
        "February": "Февраля",
        "March": "Марта",
        "April": "Апреля",
        "May": "Мая",
        "June": "Июня",
        "July": "Июля",
        "August": "Августа",
        "September": "Сентября",
        "October": "Октября",
        "November": "Ноября",
        "December": "Декабря",
    }

    for key, value in months.items():
        date_str = date_str.replace(key, value)

    week_days: dict[str, str] = {
        "Monday": "Понедельник",
        "Tuesday": "Вторник",
        "Wednesday": "Среда",
        "Thursday": "Четверг",
        "Friday": "Пятница",
        "Saturday": "Суббота",
        "Sunday": "Воскресенье",
    }

    for key, value in week_days.items():
        date_str = date_str.replace(key, value)

    return date_str


def is_same_day(date1: datetime, date2: datetime) -> bool:
    return date1.date() == date2.date()


def get_date_time(date: datetime) -> tuple[int, int]:
    return date.hour * 60 + date.minute


@cachetools.cached(cache=cachetools.LRUCache(2500))
def get_lesson_num_by_time(target_time: int | None = None) -> tuple[bool, int] | None:
    """
    Функция возвращает номер пары и перерыв ли, либо None, если время неучебное

    Args:
        target_time: время в минутах (int | None), если None, то берется текущее

    Returns:
        tuple[bool, int] | None: кортеж, где первый элемент – перемена ли это, а второй – номер пары
    """

    base_time = target_time if target_time is not None else now()
    cur_time: int = get_date_time(base_time)

    lessons: list[tuple[int, dict[str, int]]] = sorted(PAIRS_TIMES.items())

    first_start: int = lessons[0][1]["time_start"]
    if cur_time < first_start:
        return None

    for idx, (lesson_num, times) in enumerate(lessons):
        start: int = times["time_start"]
        end: int = times["time_end"]

        if start <= cur_time < end:
            return False, lesson_num

        if idx + 1 < len(lessons):
            next_start: int = lessons[idx + 1][1]["time_start"]

            if end <= cur_time < next_start:
                return True, lessons[idx + 1][0]
    return None
