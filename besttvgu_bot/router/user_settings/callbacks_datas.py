from aiogram.filters.callback_data import CallbackData


class CallSettingCallbackData(CallbackData, prefix="setting"):
    setting_name: str
