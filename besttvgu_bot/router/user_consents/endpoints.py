from aiogram import Router
from aiogram.types import CallbackQuery, InlineKeyboardButton

from besttvgu_bot.api_contracts.pdn.contracts import accept_user_consents
from besttvgu_bot.config import USER_CONSENTS
from besttvgu_bot.consts import Templates
from besttvgu_bot.middlewares import AcceptingConsentsCallbackData
from besttvgu_bot.misc.caching import user_consents_cache, CacheIdentifiers
from besttvgu_bot.misc.jinja import answer_by_template
from besttvgu_bot.misc.replies import build_reply_keyboard
from besttvgu_bot.router.user_consents.callbacks_datas import GiveConsentsCallbackData
from besttvgu_bot.router.user_consents.misc import send_consent_agreeing

router: Router = Router(name="user_consents")


@router.callback_query(AcceptingConsentsCallbackData.filter())
async def handle_call_setting(
        callback_query: CallbackQuery,
        callback_data: AcceptingConsentsCallbackData
) -> None:
    if callback_data.is_consents_accepted:
        await accept_user_consents(callback_query.from_user.id)

        await answer_by_template(
            callback_query.message,
            template_name=Templates.USER_ACCEPTED_CONSENTS,
            edit=True
        )
        user_consents_cache[CacheIdentifiers.check_user_consents(callback_query.from_user.id)] = True

        await callback_query.answer("Согласие принято ✅")
    else:
        consent_reminding_buttons: list[InlineKeyboardButton] = [
            InlineKeyboardButton(
                text="🙃 Передумал",
                callback_data=GiveConsentsCallbackData().pack()
            )
        ]

        await answer_by_template(
            callback_query.message,
            template_name=Templates.NOT_ACCEPTING_CONSENTS,
            reply_markup=build_reply_keyboard(consent_reminding_buttons, row_width=1)
        )
        await callback_query.answer("Согласие отклонено ❌")

    for i in range(1, len(USER_CONSENTS) + 1):
        try:
            await callback_query.bot.delete_message(
                callback_query.from_user.id,
                callback_query.message.message_id - i
            )
        except Exception:
            pass


@router.callback_query(GiveConsentsCallbackData.filter())
async def handle_call_setting(
        callback_query: CallbackQuery
) -> None:
    await send_consent_agreeing(callback_query.message)
    await callback_query.message.delete()
