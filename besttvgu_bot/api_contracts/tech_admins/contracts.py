from besttvgu_bot.api_contracts.api_requests import api_get
from besttvgu_bot.api_contracts.models import UserTechPublic
from besttvgu_bot.api_contracts.tech_admins.models import TechAdminsAPI


# todo: Закешировать, но обязательно с TTL
async def get_tech_admins() -> list[UserTechPublic]:
    tech_admins_resp: TechAdminsAPI = await api_get(
        "get_tech_admins",
        TechAdminsAPI
    )

    return tech_admins_resp.tech_admins
