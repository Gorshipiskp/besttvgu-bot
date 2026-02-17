from aiogram import Bot, Dispatcher

from besttvgu_bot.bot import create_bot
from besttvgu_bot.config import bot_settings
from besttvgu_bot.dispatcher import create_dispatcher, setup_routers
from besttvgu_bot.misc.logger import logger
from besttvgu_bot.modules.commands import default_commands
from besttvgu_bot.modules.pdn_handler import init_pdn


async def start_besttvgu_bot() -> None:
    bot: Bot = create_bot(bot_settings.bot_token)
    dp: Dispatcher = create_dispatcher()
    setup_routers(dp)

    await bot.set_my_commands(default_commands)

    init_pdn()

    try:
        logger.info("Bot started")
        await dp.start_polling(bot)
    finally:
        await bot.session.close()
        logger.info("Bot stopped")
