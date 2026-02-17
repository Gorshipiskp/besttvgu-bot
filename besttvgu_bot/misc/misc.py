import inspect
import re
from datetime import datetime, time
from typing import TypeVar, Awaitable, Callable

from aiogram.exceptions import TelegramBadRequest
from aiogram.methods import SendMessage
from aiogram.types import Message, Update

from besttvgu_bot.misc.datetime_lib import now


def clean_str(text: str, good_symbols: re.Pattern) -> str:
    return re.sub(f"[^{good_symbols}]+", "", text).strip()


async def safe_answer(message: Message | Update, text: str, edit: bool = False, **kwargs) -> SendMessage:
    """
    Функция отправки ответа текстовым сообщением.
    Используем эту функцию для того, чтобы отправлять сообщения централизованно и не забывать про отключение
    уведомлений

    Args:
        message: Сообщение для ответа (или объект `Update`)
        text: Текст для ответа
        edit: Нужно ли заменить сообщение, а не отправлять новое
        kwargs: Опциональные аргументы

    Returns:
        Экземпляр отправленного сообщения (`SendMessage`)
    """

    # С 23:00 по 8:00
    is_night: bool = time(hour=23) < now().time() or now().time() <= time(hour=8)

    if edit:
        try:
            return await message.edit_text(
                text,
                **kwargs
            )
        except TelegramBadRequest as e:
            if "message is not modified" in e.message:
                return
            else:
                raise e
    else:
        return await message.answer(
            text,
            disable_notification=is_night,
            **kwargs
        )


T = TypeVar("T")


async def maybe_async(func: Callable[..., T | Awaitable[T]] | T, *args, **kwargs) -> T:
    """
    Универсальный запуск sync и async функций.
    Всегда используется через await.
    """

    if inspect.iscoroutinefunction(func):
        return await func(*args, **kwargs)
    if inspect.iscoroutine(func):
        return await func
    if not inspect.isfunction(func):
        return func

    result: T = func(*args, **kwargs)

    if inspect.isawaitable(result):
        return await result

    return result


def format_timestamp(time: int) -> str:
    hours: int = time // 60
    minutes: int = time % 60

    return f"{hours:02}:{minutes:02}"
