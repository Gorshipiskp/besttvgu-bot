from typing import Any, Callable, Awaitable, TypeVar

from aiogram import BaseMiddleware
from aiogram.types import Update, Message

T = TypeVar("T")


class AdminCheckMiddleware(BaseMiddleware):
    async def __call__(
            self,
            handler: Callable[[Update | Message, dict[str, Any]], Awaitable[T]],
            update: Update | Message,
            data: dict[str, Any]
    ) -> T:
        print(data["user"])

        return await handler(update, data)
