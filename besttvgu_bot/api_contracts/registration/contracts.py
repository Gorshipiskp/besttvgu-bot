from besttvgu_bot.api_contracts.api_requests import api_post
from besttvgu_bot.api_contracts.models import UserFullPublic
from besttvgu_bot.api_contracts.registration.models import UserToRegister


async def register_user(user: UserToRegister) -> UserFullPublic:
    return await api_post(
        "registration",
        user.model_dump(),
        UserFullPublic
    )
