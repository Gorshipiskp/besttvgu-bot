import httpx

from besttvgu_bot.api_contracts.api_requests import api_post
from besttvgu_bot.api_contracts.models import UserFull


async def get_user_contract(telegram_id: int) -> UserFull | None:
    try:
        user: UserFull = await api_post(
            "user",
            {"telegram_id": telegram_id},
            UserFull
        )
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 404:
            return None
        raise e
    return user
