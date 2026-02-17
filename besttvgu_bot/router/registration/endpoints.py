import asyncio
from typing import Any

from aiogram import Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, BotCommand

from besttvgu_bot.api_contracts.models import UserFullPublic
from besttvgu_bot.api_contracts.registration.contracts import register_user
from besttvgu_bot.api_contracts.registration.models import UserToRegister
from besttvgu_bot.consts import Templates
from besttvgu_bot.middlewares import update_user
from besttvgu_bot.misc.jinja import answer_by_template
from besttvgu_bot.misc.logger import logger
from besttvgu_bot.misc.misc import safe_answer
from besttvgu_bot.misc.replies import cancel_kb
from besttvgu_bot.modules.commands import register_command, CommandAccessibilityInfo, InfoAvailability, \
    update_user_commands
from besttvgu_bot.modules.errors_handler import send_error_report
from besttvgu_bot.router.registration.middlewares import ServicesMiddleware, RegistrationService, Registration

router: Router = Router(name="registration")

router.message.middleware(
    ServicesMiddleware(registration_service=RegistrationService())
)

register_command(
    CommandAccessibilityInfo(
        need_registration=InfoAvailability.NO,
        min_role_level=10,
        max_role_level=99
    ),
    BotCommand(
        command="register",
        description="Регистрация"
    )
)


@router.message(Command("register"))
async def start_register(
        message: Message,
        is_registered: bool,
        state: FSMContext,
        service: RegistrationService
) -> None:
    if is_registered:
        await answer_by_template(
            message=message,
            template_name=Templates.ALREADY_REGISTERED,
        )
        return

    prompt: str | None = await service.start(message.from_user, state)

    if prompt:
        await safe_answer(message, prompt, reply_markup=cancel_kb)
    else:
        await finish_registration(message, state)


@router.message(Registration.active)
async def register_step(message: Message, state: FSMContext, service: RegistrationService) -> None:
    prompt: str | None = await service.process_input(message.text, state)

    if prompt:
        await safe_answer(message, prompt, reply_markup=cancel_kb)
    else:
        await finish_registration(message, state)


async def finish_registration(message: Message, state: FSMContext) -> None:
    data: dict[str, Any] = await state.get_data()

    try:
        new_user: UserFullPublic = await register_user(
            UserToRegister(
                telegram_id=message.from_user.id,
                username=data.get("username"),
                firstname=data.get("firstname"),
                lastname=data.get("lastname"),
                patronymic=data.get("patronymic"),
            )
        )

        await answer_by_template(
            message=message,
            template_name=Templates.ON_REGISTRATION,
            template_params={
                "new_user": new_user
            }
        )

        logger.info(f"User {message.from_user.id} registered")

        await update_user_commands(new_user, message)
    except Exception as e:
        await safe_answer(message, "<b>Регистрация не удалась, попробуйте позже ❌</b>")

        logger.critical(f"User {message.from_user.id} failed to register")

        await send_error_report(
            bot=message.bot,
            exception=e,
            context={
                "user_id": message.from_user.id,
                "fsm_data": data,
            },
            message=message
        )
    finally:
        await state.clear()

        # Делаем prefetch, чтобы потом не тратить время на это
        asyncio.create_task(
            update_user(message)
        )
