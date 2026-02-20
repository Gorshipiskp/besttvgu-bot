import asyncio
from dataclasses import dataclass
from enum import Enum

from aiogram.types import BotCommand, Message, BotCommandScopeChat

from besttvgu_bot.api_contracts.models import UserFull
from besttvgu_bot.misc.logger import logger

# Это команды, доступные всем (вне зависимости ни от чего)
default_commands: list[BotCommand] = [
    BotCommand(command="/start", description="Старт"),
]


class InfoAvailability(Enum):
    YES = "YES"
    NO = "NO"
    NOT_MATTER = "NOT_MATTER"


@dataclass(kw_only=True, frozen=True)
class CommandAccessibilityInfo:
    need_registration: InfoAvailability
    min_role_level: int | None = None
    max_role_level: int | None = None


all_commands: dict[BotCommand, CommandAccessibilityInfo] = {}


def register_command(access_info: CommandAccessibilityInfo, command: BotCommand) -> None:
    all_commands[command] = access_info


def availability_command_for_user(user_level: int | None, access_info: CommandAccessibilityInfo) -> bool:
    is_user_registered: bool = user_level is not None

    if access_info.need_registration == InfoAvailability.NO:
        if is_user_registered:
            return False

    if access_info.need_registration == InfoAvailability.YES:
        if not is_user_registered:
            return False

    if user_level is None:
        logger.warning(f"`user_level` must be not None")
        return False

    return access_info.min_role_level <= user_level <= access_info.max_role_level


def get_suitable_commands_for_user(user: UserFull | None) -> list[BotCommand]:
    commands: list[BotCommand] = [*default_commands]
    user_role_level: int | None = None if user is None else user.role.level

    for command, access_info in all_commands.items():
        if availability_command_for_user(user_role_level, access_info):
            commands.append(command)

    return commands


async def update_user_commands(user: UserFull | None, message: Message) -> None:
    suitable_commands: list[BotCommand] = get_suitable_commands_for_user(user)

    # todo: Тут потом либо навесим условия для аккуратного изменения команд, чтобы не делать лишние запросы,
    #  либо вот так (скидывать на фон)
    asyncio.create_task(
        message.bot.set_my_commands(
            suitable_commands,
            scope=BotCommandScopeChat(chat_id=message.from_user.id)
        )
    )
