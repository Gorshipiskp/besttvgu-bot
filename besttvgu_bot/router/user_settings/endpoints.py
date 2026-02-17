from aiogram import Router
from aiogram.filters import Command
from aiogram.types import CallbackQuery, Message, InlineKeyboardButton

from besttvgu_bot.api_contracts.models import UserFullPublic
from besttvgu_bot.consts import Templates
from besttvgu_bot.misc.jinja import answer_by_template
from besttvgu_bot.misc.replies import build_reply_keyboard
from besttvgu_bot.modules.user_settings import UserSetting, add_user_setting, USER_SETTINGS_BY_CODE, USER_SETTINGS
from besttvgu_bot.router.user_settings.callbacks_datas import CallSettingCallbackData
from besttvgu_bot.router.user_settings.misc import format_user_group, send_choose_group

router: Router = Router(name="user_settings")

add_user_setting(
    UserSetting(
        code="cur_group_id",
        display_name="Текущая группа",
        description="Группа, информация о которой будет использоваться",
        format=format_user_group,
        call_handler=send_choose_group
    )
)


@router.callback_query(CallSettingCallbackData.filter())
async def handle_call_setting(
        callback_query: CallbackQuery,
        callback_data: CallSettingCallbackData,
        user: UserFullPublic
) -> None:
    if callback_data.setting_name not in USER_SETTINGS_BY_CODE:
        return

    setting: UserSetting = USER_SETTINGS_BY_CODE[callback_data.setting_name]
    await setting.call_handler(callback_query.message, user)


@router.message(Command("settings"))
async def settings(message: Message, user: UserFullPublic, edit: bool = False) -> None:
    settings_buttons: list[InlineKeyboardButton] = [
        InlineKeyboardButton(
            text=setting.display_name,
            callback_data=CallSettingCallbackData(setting_name=setting.code).pack()
        ) for setting in USER_SETTINGS
    ]

    await answer_by_template(
        message,
        Templates.SETTINGS,
        {
            "user": user,
            "user_settings": USER_SETTINGS,
            "cur_settings": user.telegram_settings
        },
        reply_markup=build_reply_keyboard(settings_buttons, 3),
        edit=edit
    )
