from pydantic import BaseModel

from besttvgu_bot.api_contracts.models import UserTechPublic


class TechAdminsAPI(BaseModel):
    tech_admins: list[UserTechPublic]

    model_config = {"frozen": True}
