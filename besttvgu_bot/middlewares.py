import time
from typing import Any, TypeVar, Callable, Awaitable

from aiogram import BaseMiddleware
from aiogram.filters.callback_data import CallbackData
from aiogram.types import Message, Update

from besttvgu_bot.api_contracts.models import UserFull
from besttvgu_bot.api_contracts.pdn.contracts import check_user_consents_contract
from besttvgu_bot.api_contracts.user.contracts import get_user_contract
from besttvgu_bot.config import SHOW_MIDDLEWARES_PERFORMANCE, TELEGRAM_CHANNEL_LINK, WEBSITE_URL
from besttvgu_bot.consts import Templates
from besttvgu_bot.misc.caching import user_cache, CacheIdentifiers, user_consents_cache
from besttvgu_bot.misc.jinja import answer_by_template
from besttvgu_bot.misc.logger import logger
from besttvgu_bot.modules.commands import update_user_commands
from besttvgu_bot.modules.performance_metrics import BotPerformanceMiddleware
from besttvgu_bot.router.user_consents.misc import send_consent_agreeing

T = TypeVar("T")


class AcceptingConsentsCallbackData(CallbackData, prefix="accept_consents"):
    is_consents_accepted: bool


class CheckRegisterMiddleware(BaseMiddleware):
    async def __call__(
            self,
            handler: Callable[[Update | Message, dict[str, Any]], Awaitable[T]],
            update: Update | Message,
            data: dict[str, Any]
    ) -> T:
        # todo: В будущем сделаем возможность просмотра расписания без непосредственного
        #  вступления в группу и регистрации
        if data["user"] is None:
            await answer_by_template(
                update,
                Templates.NOT_REGISTERED
            )

            return

        async def check_user_consents_kruto() -> bool:
            return await check_user_consents_contract(update.from_user.id)

        is_consents_accepted: bool = await user_consents_cache.get_or_set(
            CacheIdentifiers.check_user_consents(update.from_user.id),
            check_user_consents_kruto
        )

        if not is_consents_accepted:
            await send_consent_agreeing(update)
            await update.bot.delete_message(update.chat.id, update.message_id)

            return

        return await handler(update, data)


class PerformanceMiddlewareBase(BaseMiddleware):
    async def __call__(
            self,
            handler: Callable[[Update | Message, dict[str, Any]], Awaitable[T]],
            event: Update | Message,
            data: dict[str, Any]
    ) -> T:
        start: float = time.perf_counter()

        await self.middleware_logic(event, data=data)

        end: float = time.perf_counter()
        duration: float = (end - start) * 1000

        if duration > 600:
            logger.warning(
                f"[{self.__class__.__name__}] Execution time: {duration:.3f} ms"
            )

        if SHOW_MIDDLEWARES_PERFORMANCE:
            print(f"[{self.__class__.__name__}] Execution time: {duration:.3f} ms")

        return await handler(event, data)

    async def middleware_logic(self, event: Update | Message, data: dict[str, Any]) -> None:
        """
        Переопределяется в наследниках.
        Не должен вызывать handler.
        """
        pass


class GeneralInfoMiddlewareBase(PerformanceMiddlewareBase):
    async def middleware_logic(self, event: Update | Message, data: dict[str, Any]) -> None:
        data["telegram_channel_link"] = TELEGRAM_CHANNEL_LINK
        data["website_url"] = WEBSITE_URL


async def update_user(message: Message) -> UserFull | None:
    async def user_get():
        return await get_user_contract(message.from_user.id)

    return await user_cache.get_or_set(
        CacheIdentifiers.user_info(message.from_user.id),
        user_get
    )


async def get_user_kruto_data(message: Message, data: dict[str, Any]) -> None:
    data["user"] = await update_user(message)
    data["is_registered"] = data["user"] is not None
    data["is_in_groups"] = False if data["user"] is None else len(data["user"].groups) > 0


class UserInfoMiddlewareBase(PerformanceMiddlewareBase):
    async def middleware_logic(self, message: Message, data: dict[str, Any]):
        await get_user_kruto_data(message, data)


class PerformanceMessageHandler(PerformanceMiddlewareBase):
    def __init__(self, profiler: BotPerformanceMiddleware):
        super().__init__()

        self.profiler: BotPerformanceMiddleware = profiler

    async def __call__(
            self,
            handler: Callable[[Update | Message, dict[str, Any]], Awaitable[T]],
            message: Message,
            data: dict[str, Any]
    ) -> T:
        name: str = getattr(message, "message", None) and message.text or "unknown"

        return await self.profiler.measure("message", name, handler, message, data)


class UserCommandsMiddleware(PerformanceMiddlewareBase):
    async def middleware_logic(self, message: Message, data: dict) -> None:
        user: UserFull | None = data.get("user", False)

        if user is False:
            raise RuntimeError(
                "UserCommandsMiddleware requires UserMiddleware to be registered before it"
            )

        await update_user_commands(user, message)
