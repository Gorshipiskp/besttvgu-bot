from aiogram import Router
from aiogram.filters import BaseFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, ReplyKeyboardRemove

from besttvgu_bot.misc.misc import safe_answer

router: Router = Router(name="cancel")


class CancelFilter(BaseFilter):
    async def __call__(self, message: Message) -> bool:
        return message.text in {"Отмена", "/cancel"}


@router.message(CancelFilter())
async def cancel_any_state(message: Message, state: FSMContext):
    await state.clear()

    await safe_answer(message, "Ок", reply_markup=ReplyKeyboardRemove())
