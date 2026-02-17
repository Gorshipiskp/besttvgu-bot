import httpx

from besttvgu_bot.api_contracts.api_requests import api_post
from besttvgu_bot.api_contracts.models import UserFullPublic


async def get_user(telegram_id: int) -> UserFullPublic | None:
    try:
        user: UserFullPublic = await api_post(
            "user",
            {"telegram_id": telegram_id},
            UserFullPublic
        )
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 404:
            return None
        raise e
    return user
