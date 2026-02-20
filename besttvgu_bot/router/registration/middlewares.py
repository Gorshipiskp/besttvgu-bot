from typing import Any, Final

from aiogram import BaseMiddleware
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import User

from besttvgu_bot.api_contracts.models import USERNAME_SYMBOLS, USERNAME_RE, FIRSTNAME_SYMBOLS, FIRSTNAME_RE, \
    LASTNAME_SYMBOLS, LASTNAME_RE
from besttvgu_bot.misc.misc import clean_str

REQUIRED_FIELDS: Final[dict[str, dict[str, Any]]] = {
    "username": {
        "tg_attr": "username",
        "label": "Некорректный никнейм",
        "ask": "<b>Введите никнейм</b>",
        "good_symbols": USERNAME_SYMBOLS,
        "pattern": USERNAME_RE,
    },
    "firstname": {
        "tg_attr": "first_name",
        "label": "Некорректное имя",
        "ask": "<b>Введите имя</b>",
        "good_symbols": FIRSTNAME_SYMBOLS,
        "pattern": FIRSTNAME_RE,
    },
    "lastname": {
        "tg_attr": "last_name",
        "label": "Некорректная фамилия",
        "ask": "<b>Введите фамилию</b>",
        "good_symbols": LASTNAME_SYMBOLS,
        "pattern": LASTNAME_RE,
    }
}


class Registration(StatesGroup):
    active = State()


class RegistrationService:
    async def start(self, user: User, state: FSMContext):
        await state.set_state(Registration.active)

        data: dict[str, Any] = {}

        for field, cfg in REQUIRED_FIELDS.items():
            tg_value: str | None = getattr(user, cfg["tg_attr"], None)
            tg_value: str | None = None if tg_value is None else clean_str(tg_value, cfg["good_symbols"])

            if tg_value:
                data[field] = tg_value

        await state.update_data(**data)

        return await self.ask_next(state)

    async def process_input(self, text: str, state: FSMContext):
        data = await state.get_data()

        for field, cfg in REQUIRED_FIELDS.items():
            if field not in data:
                if not cfg["pattern"].fullmatch(text):
                    return f"<b>{cfg['label']}, попробуйте ещё раз</b>"

                await state.update_data(**{field: clean_str(text, cfg["good_symbols"])})
                return await self.ask_next(state)

    @staticmethod
    async def ask_next(state: FSMContext):
        data: dict[str, Any] = await state.get_data()

        for field, cfg in REQUIRED_FIELDS.items():
            if field not in data:
                return cfg["ask"]

        return None


class RegistrationServicesMiddleware(BaseMiddleware):
    def __init__(self, registration_service: RegistrationService):
        self.registration_service: RegistrationService = registration_service

    async def __call__(self, handler, event, data):
        data["reg_service"] = self.registration_service
        return await handler(event, data)
