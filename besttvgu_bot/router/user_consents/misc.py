from aiogram.filters.callback_data import CallbackData
from aiogram.types import BufferedInputFile, InlineKeyboardButton, Update, Message

from besttvgu_bot.config import USER_CONSENTS
from besttvgu_bot.consts import Templates
from besttvgu_bot.misc.jinja import render_template
from besttvgu_bot.misc.misc import safe_answer
from besttvgu_bot.misc.replies import build_reply_keyboard


class AcceptingConsentsCallbackData(CallbackData, prefix="accept_consents"):
    is_consents_accepted: bool


async def send_consent_agreeing(message: Message | Update) -> None:
    template_rendered: str = render_template(Templates.NEED_TO_ACCEPT_CONSENTS)

    documents_handler = message.bot.documents_handler

    consent_accepting_buttons: list[InlineKeyboardButton] = [
        InlineKeyboardButton(
            text="✅ Согласен",
            callback_data=AcceptingConsentsCallbackData(is_consents_accepted=True).pack()
        ),
        InlineKeyboardButton(
            text="❌ Не согласен",
            callback_data=AcceptingConsentsCallbackData(is_consents_accepted=False).pack()
        )
    ]

    for consent_name, consent in USER_CONSENTS.items():
        await message.bot.send_document(
            chat_id=message.chat.id,
            document=BufferedInputFile(
                await documents_handler.get_document_bytes_by_name(consent_name),
                filename=documents_handler.get_document_fullname(consent_name),
            ),
            caption=consent["name"]
        )

    await safe_answer(
        message,
        template_rendered,
        reply_markup=build_reply_keyboard(consent_accepting_buttons, row_width=2)
    )
