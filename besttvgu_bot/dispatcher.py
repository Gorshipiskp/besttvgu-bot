from aiogram import Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

from besttvgu_bot.middlewares import UserInfoMiddlewareBase, PerformanceMessageHandler, UserCommandsMiddleware, \
    GeneralInfoMiddlewareBase
from besttvgu_bot.modules.errors_handler import router as errors_router
from besttvgu_bot.modules.performance_metrics import BotPerformanceMiddleware
from besttvgu_bot.router.cancel.endpoints import router as cancel_router
from besttvgu_bot.router.general.endpoints import router as general_router
from besttvgu_bot.router.group.endpoints import router as group_router
from besttvgu_bot.router.registration.endpoints import router as registration_router
from besttvgu_bot.router.user_consents.endpoints import router as user_consents_router
from besttvgu_bot.router.user_settings.endpoints import router as user_settings_router
from besttvgu_bot.router.user.endpoints import router as user_router


def create_dispatcher() -> Dispatcher:
    storage: MemoryStorage = MemoryStorage()

    dp: Dispatcher = Dispatcher(storage=storage)

    profiler: BotPerformanceMiddleware = BotPerformanceMiddleware()

    dp.message.middleware(UserInfoMiddlewareBase())
    dp.callback_query.middleware(UserInfoMiddlewareBase())

    # `UserCommandsMiddleware` должен быть ниже `UserInfoMiddleware`
    dp.message.middleware(UserCommandsMiddleware())

    dp.message.middleware(GeneralInfoMiddlewareBase())
    dp.callback_query.middleware(GeneralInfoMiddlewareBase())

    # `PerformanceMessageHandler` должен стоять последним
    dp.message.middleware(PerformanceMessageHandler(profiler))

    return dp


def setup_routers(dp: Dispatcher) -> None:
    # Лучше первым
    dp.include_router(errors_router)

    # `cancel_router` Должен быть первым
    dp.include_router(cancel_router)

    dp.include_router(general_router)
    dp.include_router(registration_router)
    dp.include_router(group_router)
    dp.include_router(user_settings_router)
    dp.include_router(user_consents_router)
    dp.include_router(user_router)
