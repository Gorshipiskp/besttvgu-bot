
from aiogram.methods import SendMessage
from aiogram.types import InlineKeyboardButton, Message

from besttvgu_bot.api_contracts.models import UserFullPublic
from besttvgu_bot.misc.misc import safe_answer
from besttvgu_bot.misc.replies import build_reply_keyboard
from besttvgu_bot.router.group.callbacks_datas import ChooseGroupCallbackData


async def send_choose_group(message: Message, user: UserFullPublic) -> SendMessage:
    groups_buttons: list[InlineKeyboardButton] = [
        InlineKeyboardButton(
            text=group.name,
            callback_data=ChooseGroupCallbackData(group_id=group.id).pack()
        ) for group in user.groups
    ]

    return await safe_answer(
        message,
        "<b>У вас несколько групп, выберите нужную</b>",
        reply_markup=build_reply_keyboard(groups_buttons, 2),
        edit=True
    )


def format_user_group(user: UserFullPublic) -> str:
    return "Не указана" if user.telegram_settings.cur_group is None else user.telegram_settings.cur_group.name
