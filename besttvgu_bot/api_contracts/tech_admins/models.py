from pydantic import BaseModel

from besttvgu_bot.api_contracts.models import UserTech


class TechAdminsAPI(BaseModel):
    tech_admins: list[UserTech]

    model_config = {"frozen": True}
