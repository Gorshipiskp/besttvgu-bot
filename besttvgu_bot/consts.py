from enum import Enum
from logging import INFO, WARNING, ERROR, CRITICAL
from typing import Final


class Templates(str, Enum):
    START = "start_message.html"
    ON_REGISTRATION = "on_registration.html"
    ALREADY_REGISTERED = "already_registered.html"
    NO_GROUPS = "no_groups.html"
    NOT_REGISTERED = "not_registered.html"
    SETTINGS = "settings.html"
    GROUP_NO_SCHEDULE = "group_no_schedule.html"
    GROUP_SCHEDULE = "group_schedule.html"
    OOPS_SOMETHING_WENT_WRONG = "oops_something_went_wrong.html"
    NOT_SO_FAR_IN_SCHEDULE = "not_so_far_in_schedule.html"
    USER_GROUP = "user_cur_group.html"


# Насколько далеко (кол-во недель) можно пойти в расписании
MAX_WEEK_DELTA_SCHEDULE: Final[int] = 4

LEVELS_TO_LOG: dict[int, str] = {
    INFO: "info",
    WARNING: "warning",
    ERROR: "error",
    CRITICAL: "critical",
}

PDN_PREFIX: Final[str] = "Политика_конфиденциальности_BestTvGU"
PDN_VERSION: Final[str] = "v1.0"
