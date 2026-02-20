from enum import Enum
from logging import INFO, WARNING, ERROR, CRITICAL
from pathlib import Path
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
    NEED_TO_ACCEPT_CONSENTS = "need_to_accept_consents.html"
    NOT_ACCEPTING_CONSENTS = "not_accepting_consent.html"
    USER_ACCEPTED_CONSENTS = "user_accepted_consents.html"
    PROFILE = "profile.html"


# Насколько далеко (кол-во недель) можно пойти в расписании
MAX_WEEK_DELTA_SCHEDULE: Final[int] = 4

LEVELS_TO_LOG: dict[int, str] = {
    INFO: "info",
    WARNING: "warning",
    ERROR: "error",
    CRITICAL: "critical",
}

DOCUMENT_HASHES_FILE: Final[str] = "documents_hashes.json"
DOCUMENTS_DIRNAME: Final[str] = "documents"

DOCUMENTS_DIR: Final[Path] = Path(__file__).parent / DOCUMENTS_DIRNAME
DOCUMENTS_HASHES_FILE_PATH: Final[Path] = DOCUMENTS_DIR / DOCUMENT_HASHES_FILE

PAIRS_TIMES: Final[dict[int, dict[str, int]]] = {
    0: {'time_start': 510, 'time_end': 605},
    1: {'time_start': 615, 'time_end': 710},
    2: {'time_start': 730, 'time_end': 825},
    3: {'time_start': 840, 'time_end': 935},
    4: {'time_start': 955, 'time_end': 1050},
    5: {'time_start': 1065, 'time_end': 1160},
    6: {'time_start': 1170, 'time_end': 1260}
}
