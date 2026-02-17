import asyncio
import time
from collections import defaultdict, deque
from typing import Callable, TypeVar, Awaitable

# Да, `numpy`, возможно, избыточен и можно использовать `statistics`, но мне уже впадлу переписывать
import numpy as np

T = TypeVar("T")


class BotPerformanceMiddleware:
    def __init__(self):
        self.metrics: defaultdict[str, defaultdict[str, deque[float]]] = defaultdict(
            lambda: defaultdict(lambda: deque(maxlen=1000))
        )
        self._lock: asyncio.Lock = asyncio.Lock()

    async def measure(self, event_type: str, name: str, func: Callable[[...], T | Awaitable[T]], *args, **kwargs) -> T:
        start: float = time.perf_counter()
        result: T = await func(*args, **kwargs)
        duration: float = time.perf_counter() - start

        async with self._lock:
            self.metrics[event_type][name].append(duration)
        return result

    def get_stats(self, event_type: str, name: str) -> dict[str, float | int]:
        durations: list[float] = list(self.metrics[event_type][name])
        if not durations:
            return {}

        return {
            "count": len(durations),
            "avg": np.mean(durations),
            "p50": np.percentile(durations, 50),
            "p95": np.percentile(durations, 95),
            "p99": np.percentile(durations, 99)
        }

    def reset(self) -> None:
        self.metrics.clear()
