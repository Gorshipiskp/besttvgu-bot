from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message, BotCommand

from besttvgu_bot.api_contracts.models import UserFull, format_group_type, UserGroupPublic
from besttvgu_bot.consts import Templates
from besttvgu_bot.middlewares import CheckRegisterMiddleware
from besttvgu_bot.misc.jinja import answer_by_template
from besttvgu_bot.modules.commands import register_command, CommandAccessibilityInfo, InfoAvailability

router: Router = Router(name="user")

router.message.middleware(
    CheckRegisterMiddleware()
)

register_command(
    CommandAccessibilityInfo(
        need_registration=InfoAvailability.YES,
        min_role_level=10,
        max_role_level=99
    ),
    BotCommand(
        command="profile",
        description="Ваш профиль"
    )
)


@router.message(Command("profile"))
async def profile(message: Message, user: UserFull) -> None:
    groups_ids_to_user_group: dict[int, UserGroupPublic] = {}

    for group in user.groups:
        groups_ids_to_user_group[group.id] = [
            user_group for user_group in user.user_groups if user_group.group_id == group.id
        ][0]

    return await answer_by_template(
        message=message,
        template_name=Templates.PROFILE,
        template_params={
            "user": user,
            "groups_ids_to_user_group": groups_ids_to_user_group,
            "format_group_type": format_group_type
        }
    )
