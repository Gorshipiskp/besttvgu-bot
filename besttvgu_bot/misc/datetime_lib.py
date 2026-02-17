from datetime import datetime, timedelta
from zoneinfo import ZoneInfo


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
