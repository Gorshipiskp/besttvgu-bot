from besttvgu_bot.api_contracts.api_requests import api_get
from besttvgu_bot.api_contracts.models import UserTech
from besttvgu_bot.api_contracts.tech_admins.models import TechAdminsAPI


async def get_tech_admins_contract() -> list[UserTech]:
    """
    Возвращает список всех технических администраторов

    Returns:
        Список всех технических администраторов в формате `UserTechPublic`
    """
    tech_admins_resp: TechAdminsAPI = await api_get(
        "get_tech_admins",
        TechAdminsAPI
    )

    return tech_admins_resp.tech_admins
