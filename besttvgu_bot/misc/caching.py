import asyncio
from typing import Callable, Awaitable, TypeVar, Any

from cachetools import TTLCache

from besttvgu_bot.config import USER_CACHE_TTL_SECONDS, USER_AGREEMENT_CACHE_TTL_SECONDS, FULL_GROUPS_CACHE_TTL_SECONDS, \
    GROUPS_SCHEDULE_CACHE_TTL_SECONDS
from besttvgu_bot.misc.logger import logger
from besttvgu_bot.misc.misc import maybe_async

T = TypeVar("T")

all_cache: dict[str, "AsyncTTLCache"] = {}


class AsyncTTLCache:
    def __init__(self, name: str, maxsize: int, ttl: int) -> None:
        self.name = name
        self._cache = TTLCache(maxsize=maxsize, ttl=ttl)
        self._lock = asyncio.Lock()

        if name in all_cache:
            raise ValueError(f"Cache with name {name} already exists")

        logger.info(f"Created cache {name} with ttl {ttl}")
        all_cache[name] = self

    def __contains__(self, key: str) -> bool:
        return key in self._cache

    def __setitem__(self, key: str, value: Any):
        self._cache[key] = value

    def __getitem__(self, key: str) -> Any:
        return self._cache[key]

    async def get_or_set(self, key: str, factory: Callable[..., T | Awaitable[T]] | T, *args, **kwargs) -> T:
        """
        Функция отправки ответа текстовым сообщением.
        Используем эту функцию для того, чтобы отправлять сообщения централизованно и не забывать про отключение
        уведомлений

        Args:
            key: Ключ кеша
            factory: Функция, которая будет вызвана в случае отсутствия значения в кеше, и её результат
            (`T`) запишется в кеш

        Returns:
            Значение из кеша (`T`)
        """

        async with self._lock:
            if key in self:
                return self[key]

            value: T = await maybe_async(factory(*args, **kwargs))

            self[key] = value

        return value

    async def invalidate(self, key: str) -> None:
        """
        Функция инвалидации кеша, используется, например, если информация изменилась и мы это знаем

        Args:
            key: Ключ кеша

        Returns:
            None
        """

        async with self._lock:
            self._cache.pop(key, None)

    async def clear(self) -> None:
        async with self._lock:
            self._cache.clear()


class CacheIdentifiers:
    @classmethod
    def user_info(cls, telegram_id: int) -> str:
        return f"user_info_{telegram_id}"

    @classmethod
    def check_user_consents(cls, telegram_id: int) -> str:
        return f"check_user_consents_{telegram_id}"

    @classmethod
    def full_group(cls, group_id: int) -> str:
        return f"full_groups_cache_{group_id}"

    @classmethod
    def group_schedule(cls, group_id: int) -> str:
        return f"group_schedule_{group_id}"


# Разные TTL
user_cache: AsyncTTLCache = AsyncTTLCache(
    name="user_cache", maxsize=5000, ttl=USER_CACHE_TTL_SECONDS
)

user_consents_cache: AsyncTTLCache = AsyncTTLCache(
    name="user_consents_cache", maxsize=5000, ttl=USER_AGREEMENT_CACHE_TTL_SECONDS
)

full_groups_cache: AsyncTTLCache = AsyncTTLCache(
    name="full_groups_cache", maxsize=5000, ttl=FULL_GROUPS_CACHE_TTL_SECONDS
)

groups_schedules_cache: AsyncTTLCache = AsyncTTLCache(
    name="groups_schedules_cache", maxsize=5000, ttl=GROUPS_SCHEDULE_CACHE_TTL_SECONDS
)
