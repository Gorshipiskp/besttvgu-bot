from dataclasses import dataclass
from typing import Callable, Awaitable

from aiogram.types import Message, BotCommand

from besttvgu_bot.api_contracts.models import UserFull
from besttvgu_bot.modules.commands import register_command, CommandAccessibilityInfo, InfoAvailability


@dataclass(frozen=True, kw_only=True)
class UserSetting:
    code: str
    display_name: str
    description: str
    format: Callable[[UserFull], str | Awaitable[str]]
    call_handler: Callable[[Message, UserFull], Awaitable[None]]


USER_SETTINGS: list[UserSetting, ...] = []
USER_SETTINGS_BY_CODE: dict[str, UserSetting] = {}


def add_user_setting(setting: UserSetting) -> None:
    if setting.code in USER_SETTINGS_BY_CODE:
        raise ValueError(f"Setting with code \"{setting.code}\" already exists")

    USER_SETTINGS.append(setting)
    USER_SETTINGS_BY_CODE[setting.code] = setting


register_command(
    CommandAccessibilityInfo(
        need_registration=InfoAvailability.YES,
        min_role_level=10,
        max_role_level=99
    ),
    BotCommand(
        command="settings",
        description="Настройки"
    )
)
