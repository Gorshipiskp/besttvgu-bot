import json
import traceback
from datetime import datetime
from typing import Any

from aiogram import Router, Bot
from aiogram.types import ErrorEvent, BufferedInputFile, Message

from besttvgu_bot.api_contracts.models import UserTech
from besttvgu_bot.config import bot_settings
from besttvgu_bot.consts import Templates
from besttvgu_bot.misc.jinja import answer_by_template
from besttvgu_bot.misc.logger import logger
from besttvgu_bot.api_contracts.tech_admins.misc import get_tech_admins

router = Router(name="errors_handler")


async def send_error_report(
        *,
        bot: Bot,
        exception: Exception,
        context: dict[str, Any] | None = None,
        message: Message | None = None
) -> None:
    logger.exception("Unhandled exception occurred", exc_info=exception)

    if message is not None:
        try:
            await answer_by_template(
                message,
                Templates.OOPS_SOMETHING_WENT_WRONG,
            )
        except Exception as e:
            logger.exception("Unhandled exception occurred while sending notice to user", exc_info=e)

    traceback_str: str = "".join(
        traceback.format_exception(
            type(exception),
            exception,
            exception.__traceback__,
        )
    )

    error_payload: dict[str, Any] = {
        "timestamp": datetime.utcnow().isoformat(),
        "exception_type": type(exception).__name__,
        "exception_message": str(exception),
        "traceback": traceback_str,
        "context": context or {},
    }

    file_content: bytes = json.dumps(
        error_payload,
        ensure_ascii=False,
        indent=2,
        default=str,
    ).encode("UTF-8")

    try:
        tech_admins: list[UserTech] = await get_tech_admins()
    except Exception:
        logger.exception("Failed to fetch tech admins")
        return

    for admin in tech_admins:
        try:
            file = BufferedInputFile(
                file_content,
                filename=f"error_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.json",
            )

            await bot.send_document(
                chat_id=admin.telegram_id,
                document=file,
                caption="🚨 Произошла ошибка в боте",
            )
        except Exception:
            logger.exception(
                f"Failed to send error report to {admin.telegram_id}"
            )

            await bot.send_message(
                chat_id=bot_settings.creator_telegram_id,
                text=f"Ошибка при отправке отчета тех.админу {admin.telegram_id}",
            )


@router.errors()
async def global_error_handler(event: ErrorEvent) -> bool:
    await send_error_report(
        bot=event.update.bot,
        exception=event.exception,
        context={
            "update": event.update.model_dump(),
        },
        message=event.update.message
    )
    return True
