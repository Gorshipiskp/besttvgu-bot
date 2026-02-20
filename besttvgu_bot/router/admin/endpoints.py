from aiogram import Router
from aiogram.types import BotCommand

from besttvgu_bot.consts import MIN_TECH_ADMIN_LEVEL
from besttvgu_bot.middlewares import CheckRegisterMiddleware
from besttvgu_bot.modules.commands import register_command, CommandAccessibilityInfo, InfoAvailability
from besttvgu_bot.router.admin.middlewares import AdminCheckMiddleware

router: Router = Router(name="admin")

router.message.middleware(
    CheckRegisterMiddleware()
)

router.message.middleware(
    AdminCheckMiddleware()
)

register_command(
    CommandAccessibilityInfo(
        need_registration=InfoAvailability.YES,
        min_role_level=MIN_TECH_ADMIN_LEVEL,
        max_role_level=99
    ),
    BotCommand(
        command="admin",
        description="Административные инструменты"
    )
)
