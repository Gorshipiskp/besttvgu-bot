from besttvgu_bot.api_contracts.models import UserTech
from besttvgu_bot.api_contracts.tech_admins.contracts import get_tech_admins_contract
from besttvgu_bot.misc.caching import tech_admins_cache, CacheIdentifiers


async def get_tech_admins() -> list[UserTech]:
    return await tech_admins_cache.get_or_set(
        CacheIdentifiers.tech_admins,
        get_tech_admins_contract
    )
