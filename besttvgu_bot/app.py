from aiogram import Bot, Dispatcher

from besttvgu_bot.api_contracts.pdn.contracts import get_user_consents, validate_user_consents_documents
from besttvgu_bot.bot import create_bot
from besttvgu_bot.config import bot_settings
from besttvgu_bot.consts import DOCUMENTS_HASHES_FILE_PATH, DOCUMENTS_DIR
from besttvgu_bot.dispatcher import create_dispatcher, setup_routers
from besttvgu_bot.misc.logger import logger
from besttvgu_bot.modules.commands import default_commands
from besttvgu_bot.modules.documents_validator import DocumentsHandler, UserConsents


async def start_besttvgu_bot() -> None:
    bot: Bot = create_bot(bot_settings.bot_token)
    dp: Dispatcher = create_dispatcher()
    setup_routers(dp)

    await bot.set_my_commands(default_commands)

    # Список документов требуют обязательного согласования с бэкендом
    important_documents: UserConsents = await get_user_consents()
    logger.info("User consents received")

    documents_handler: DocumentsHandler = DocumentsHandler(
        documents_hashes_file_path=DOCUMENTS_HASHES_FILE_PATH,
        documents_path=DOCUMENTS_DIR,
        documents={
            "policy": important_documents.policy,
            "agreement": important_documents.agreement
        }
    )
    await documents_handler.init()
    logger.info("Documents handler initialized")

    await documents_handler.handle_documents()
    logger.info("Documents handled")

    bot.documents_handler = documents_handler

    await validate_user_consents_documents(
        policy_version=important_documents.policy.version,
        policy_hash=documents_handler.get_document_hash("policy"),
        agreement_version=important_documents.agreement.version,
        agreement_hash=documents_handler.get_document_hash("agreement"),
        hash_method=bot_settings.documents_hash_method
    )

    try:
        logger.info("Bot started")
        await dp.start_polling(bot)
    finally:
        await bot.session.close()
        logger.info("Bot stopped")
