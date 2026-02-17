from besttvgu_bot.api_contracts.api_requests import api_post
from besttvgu_bot.api_contracts.pdn.models import PDNConsent
from besttvgu_bot.consts import PDN_VERSION


async def get_pdn_consent_user(telegram_id: int) -> PDNConsent | None:
    return await api_post(
        "get_user_pdn_consent",
        {
            "telegram_id": telegram_id,
            "policy_version": PDN_VERSION,

        },
        PDNConsent
    )
