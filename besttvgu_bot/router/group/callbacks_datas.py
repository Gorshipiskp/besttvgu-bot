from aiogram.filters.callback_data import CallbackData


class ChooseGroupCallbackData(CallbackData, prefix="group"):
    group_id: int


class ScheduleMoveCallbackData(CallbackData, prefix="schedule_move"):
    datetime: str
