from typing import Callable, Any, Awaitable, TypeVar

from aiogram import BaseMiddleware
from aiogram.types import Message, Update

from besttvgu_bot.api_contracts.models import UserFull
from besttvgu_bot.consts import Templates
from besttvgu_bot.middlewares import get_user_kruto_data
from besttvgu_bot.misc.jinja import answer_by_template
from besttvgu_bot.modules.user_settings import USER_SETTINGS_BY_CODE


async def check_n_get_group_id(message: Message, user: UserFull, website_url: str) -> tuple[bool, int | None]:
    """
    Проверка пользователя на наличие групп и её выбор группы

    Сценарии возвращаемого значения:

    Если пользователь не состоит ни в одной группе, то возвращает `[False, None]`

    Если пользователь состоит в одной группе, то возвращает `[True, group_id]`

    Если пользователь состоит в нескольких группах, то возвращает `[False, None]`

    Если группа уже выбрана, то возвращает `[False, group_id]`

    Args:
        message: Сообщение типа `Message`
        user: Объект модели `UserFullPublic` (полная информация пользователя)
        website_url: Ссылка на сайт

    Returns:
        tuple[bool, int | None]: Требуется ли обновить информацию о пользователе, ID группы | None
    """

    if user.telegram_settings.cur_group_id is None:
        if len(user.groups) == 0:
            await answer_by_template(
                message,
                Templates.NO_GROUPS,
                template_params={
                    "website_url": website_url
                }
            )

            return False, None
        elif len(user.groups) == 1:
            group_id: int = user.groups[0].id

            await user.telegram_settings.update_user_settings(user, {"cur_group_id": group_id})

            return True, group_id

        await USER_SETTINGS_BY_CODE["cur_group_id"].call_handler(message, user)
        return False, None

    return False, user.telegram_settings.cur_group_id


T = TypeVar("T")


class GroupCheckMiddleware(BaseMiddleware):
    async def __call__(
            self,
            handler: Callable[[Update, dict[str, Any]], Awaitable[T]],
            message: Message,
            data: dict[str, Any]
    ) -> T:
        need_refresh, group_id = await check_n_get_group_id(message, data["user"], data["website_url"])

        if group_id is None:
            return

        if need_refresh:
            await get_user_kruto_data(message, data)

        return await handler(message, data)
