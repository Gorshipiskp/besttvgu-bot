from pydantic import BaseModel

from besttvgu_bot.api_contracts.models import UserUsername, UserFirstname, UserLastname, UserPatronymic


class UserToRegister(BaseModel):
    telegram_id: int
    username: UserUsername
    firstname: UserFirstname
    lastname: UserLastname
    patronymic: UserPatronymic | None = None

    model_config = {"frozen": True}
