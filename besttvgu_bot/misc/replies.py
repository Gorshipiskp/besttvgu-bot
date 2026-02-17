from aiogram.types import ReplyKeyboardMarkup, InlineKeyboardMarkup, KeyboardButton, InlineKeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder


def build_reply_keyboard(
        buttons: list[KeyboardButton | InlineKeyboardButton],
        row_width: int,
        resize_keyboard: bool = True
) -> ReplyKeyboardMarkup | InlineKeyboardMarkup:
    if len(buttons) == 0:
        raise ValueError("Given 0 buttons, this should not be possible (function `build_reply_keyboard`)")

    builder = InlineKeyboardBuilder() if isinstance(buttons[0], InlineKeyboardButton) else ReplyKeyboardBuilder()
    builder.add(*buttons)
    builder.adjust(row_width)

    return builder.as_markup(resize_keyboard=resize_keyboard)


cancel_kb: ReplyKeyboardMarkup = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Отмена")]
    ],
    resize_keyboard=True,
    one_time_keyboard=True,
)
