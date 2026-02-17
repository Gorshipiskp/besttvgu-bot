from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from besttvgu_bot.consts import Templates
from besttvgu_bot.misc.jinja import answer_by_template

router: Router = Router(name="general")


@router.message(Command("start"))
async def start(message: Message, **kwargs) -> None:
    return await answer_by_template(
        message=message,
        template_name=Templates.START,
        template_params=kwargs
    )
