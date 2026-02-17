# Здесь модели напрямую с бэкенда

import re
from enum import Enum
from typing import Literal, Final, Annotated, Any

from aiogram.types import DateTime
from pydantic import BaseModel, Field, StringConstraints

from besttvgu_bot.api_contracts.api_requests import api_post
from besttvgu_bot.misc.caching import CacheIdentifiers, user_cache

USERNAME_SYMBOLS: Final[str] = r"A-Za-zа-яА-ЯёЁ0-9_\-.–—"
USERNAME_RE: Final[re.Pattern] = re.compile(r"^[%s]{2,35}$" % USERNAME_SYMBOLS)

FIRSTNAME_SYMBOLS: Final[str] = r"а-яА-ЯёЁ\-"
FIRSTNAME_RE: Final[re.Pattern] = re.compile(r"^[%s]{2,35}$" % FIRSTNAME_SYMBOLS)

LASTNAME_SYMBOLS: Final[str] = r"а-яА-ЯёЁ\-"
LASTNAME_RE: Final[re.Pattern] = re.compile(r"^[%s]{2,35}$" % LASTNAME_SYMBOLS)

PATRONYMIC_SYMBOLS: Final[str] = r"а-яА-ЯёЁ\-"
PATRONYMIC_RE: Final[re.Pattern] = re.compile(r"^[%s]{2,35}|$" % PATRONYMIC_SYMBOLS)

UserUsername = Annotated[
    str,
    StringConstraints(
        pattern=USERNAME_RE,
        strip_whitespace=True
    ),
]

UserFirstname = Annotated[
    str,
    StringConstraints(
        pattern=FIRSTNAME_RE,
        strip_whitespace=True
    ),
]

UserLastname = Annotated[
    str,
    StringConstraints(
        pattern=LASTNAME_RE,
        strip_whitespace=True
    )
]

UserPatronymic = Annotated[
    str,
    StringConstraints(
        pattern=PATRONYMIC_RE,
        strip_whitespace=True
    )
]


class DormitoryPublic(BaseModel):
    id: int
    name: str
    address: str

    model_config = {"frozen": True}


class PlacePublic(BaseModel):
    id: int
    name: str
    is_link: bool

    model_config = {"frozen": True}


class SubjectTypes(Enum):
    LABWORK = "labwork"
    LECTURE = "lecture"
    PRACTICE = "practice"
    SEMINAR = "seminar"
    UNKNOWN = "unknown"


SUBJECT_TYPES: Final[dict[SubjectTypes, list[str]]] = {
    SubjectTypes.LECTURE: ["Лекция"],
    SubjectTypes.LABWORK: ["Лаб. работа"],
    SubjectTypes.PRACTICE: ["Практика", "Практическое занятие"],
    SubjectTypes.SEMINAR: ["Семинар"],
    SubjectTypes.UNKNOWN: ["Другое"],
}


class SubjectPublic(BaseModel):
    id: int
    name: str
    type: SubjectTypes

    model_config = {"frozen": True}


class RolePublic(BaseModel):
    id: int
    name: str
    display_name: str
    level: int
    description: str
    permissions: dict[str, dict[str, bool]]

    model_config = {"frozen": True}


class TeacherBase(BaseModel):
    id: int
    initials: str

    model_config = {"frozen": True}


class TeacherSmallPublic(TeacherBase):
    is_small_teacher: Literal[True] = True

    name: str | None = None
    surname: str | None = None
    patronymic: str | None = None
    lms_profile_link: str | None = None
    current_job: str | None = None
    experience_age: int | None = None
    email: str | None = None
    level_education: str | None = None

    def format_name(self) -> str:
        return self.initials


class TeacherFullPublic(TeacherBase):
    is_small_teacher: Literal[False] = False

    name: str
    surname: str
    patronymic: str
    lms_profile_link: str | None
    current_job: str | None
    experience_age: int | None
    email: str | None
    level_education: str | None

    def format_name(self) -> str:
        return f"{self.surname} {self.name} {self.patronymic}"


TeacherPublic = TeacherFullPublic | TeacherSmallPublic


class StructTypes(Enum):
    FACULTY = "faculty"
    INSTITUTE = "institute"


class StructPublic(BaseModel):
    id: int
    name: str
    shortname: str
    code: str
    additional_code: str | None
    boss_id: int | None
    description: str | None
    type: StructTypes
    email: str | None
    address: str | None
    postal_code: str | None
    website: str | None
    video_url: str | None

    telegram: str | None
    vkontakte: str | None
    foundation_year: int | None

    model_config = {"frozen": True}


class StructFullPublic(StructPublic):
    boss: TeacherPublic = Field(discriminator="is_small_teacher")


class GroupTypes(Enum):
    REGULAR = "regular"
    MASTER = "master"


GROUP_TYPES_NAMES: Final[dict[GroupTypes, str]] = {
    GroupTypes.REGULAR: "Бакалавриат/Специалитет",
    GroupTypes.MASTER: "Магистратура",
}


class GroupPublic(BaseModel):
    id: int
    name: str
    specialization: str | None
    number: int
    course: int
    note: str | None
    struct_id: int
    type: GroupTypes
    no_schedule: bool
    no_new_requests: bool
    academic_year: int

    model_config = {"frozen": True}


class UserGroupPublic(BaseModel):
    user_id: int
    group_id: int
    role_id: int

    role: RolePublic | None

    model_config = {"frozen": True}


class TelegramSettingsPublic(BaseModel):
    user_id: int

    cur_group_id: int | None

    cur_group: GroupPublic | None

    model_config = {"frozen": True}

    def __getitem__(self, item: str) -> Any:
        return getattr(self, item)

    def model_dump(self, exclude: Any = None, **kwargs) -> dict[str, Any]:
        """
        Переопределение метода `model_dump`, чтобы на бэкенд не попадали лишние сущности

        Args:
            exclude: Намеренно игнорируется!
            kwargs: Опциональные аргументы

        Returns:
            Словарь с настройками
        """

        return super().model_dump(exclude={
            "cur_group"
        }, **kwargs)

    async def update_user_settings(self, user: "UserFullPublic", update: dict[str, Any]) -> None:
        new_settings: TelegramSettingsPublic = self.model_copy(update=update)

        if user.telegram_settings.cur_group_id != new_settings.cur_group_id:
            if new_settings.cur_group_id is None:
                new_settings = new_settings.model_copy(update={
                    "cur_group": None
                })
            else:
                new_settings = new_settings.model_copy(update={
                    "cur_group": await get_group_info(new_settings.cur_group_id)
                })

        await api_post(
            "save_user_settings",
            {
                "user_id": user.id,
                "telegram_settings": new_settings.model_dump()
            }
        )

        # Вместо просто инвалидации аккуратно обновляем информацию, подобно реактивности в фронтенде
        user_cache[CacheIdentifiers.user_info(user.telegram_id)] = user.model_copy(
            update={
                "telegram_settings": new_settings
            }
        )


class UserPublic(BaseModel):
    id: int
    username: str
    firstname: UserFirstname | None
    lastname: UserLastname | None
    patronymic: UserPatronymic | None

    model_config = {"frozen": True}

    def format_name(self) -> str:
        if self.patronymic is None:
            return f"{self.lastname} {self.firstname}"
        else:
            return f"{self.lastname} {self.firstname} {self.patronymic}"


class GroupFullPublic(GroupPublic):
    struct: StructPublic
    users_groups: list[UserGroupPublic]
    members: list[UserPublic]


async def get_group_info(group_id: int) -> GroupFullPublic:
    return await api_post(
        "get_group_info",
        {
            "group_id": group_id
        },
        GroupPublic
    )


class UserTechPublic(UserPublic):
    telegram_id: int


class UserFullPublic(UserTechPublic):
    created_at: DateTime

    dormitory: DormitoryPublic | None
    role: RolePublic | None
    groups: list[GroupPublic]
    user_groups: list[UserGroupPublic]
    telegram_settings: TelegramSettingsPublic
