import asyncio
from typing import Callable, Awaitable, TypeVar, Any

from cachetools import TTLCache

from besttvgu_bot.config import USER_CACHE_TTL_SECONDS
from besttvgu_bot.misc.misc import maybe_async

T = TypeVar("T")


class AsyncTTLCache:
    def __init__(self, maxsize: int, ttl: int) -> None:
        self._cache = TTLCache(maxsize=maxsize, ttl=ttl)
        self._lock = asyncio.Lock()

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


# Разные TTL
user_cache: AsyncTTLCache = AsyncTTLCache(maxsize=1000, ttl=USER_CACHE_TTL_SECONDS)
