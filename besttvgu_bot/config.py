from typing import Final

from pydantic import ConfigDict
from pydantic_settings import BaseSettings


class BotSettings(BaseSettings):
    bot_token: str
    api_url: str
    bot_api_token: str
    creator_telegram_id: int
    api_request_timeout: int

    documents_hash_method: str

    model_config = ConfigDict(
        env_file=".env"
    )


bot_settings: BotSettings = BotSettings()

# Выводить ли тайминги middlewares в консоль
SHOW_MIDDLEWARES_PERFORMANCE: Final[bool] = False

# Да, многовато, но мы рассчитываем на корректную инвалидацию
USER_CACHE_TTL_SECONDS: Final[int] = 3600 * 24 * 2
USER_AGREEMENT_CACHE_TTL_SECONDS: Final[int] = 3600 * 24 * 2
FULL_GROUPS_CACHE_TTL_SECONDS: Final[int] = 3600 * 4
GROUPS_SCHEDULE_CACHE_TTL_SECONDS: Final[int] = 3600 * 24 * 1
TECH_ADMINS_CACHE_TTL_SECONDS: Final[int] = 3600 * 24 * 1

MESSAGES_TEMPLATES_DIR: Final[str] = "messages_templates"
TELEGRAM_CHANNEL_LINK: Final[str] = "https://t.me/best_tvgu"
WEBSITE_URL: Final[str] = "https://besttvgu.ru/"

USER_CONSENTS: Final[dict[str, str]] = {
    "policy": {
        "name": "Политика обработки персональных данных",
    },
    "agreement": {
        "name": "Пользовательское соглашение",
    }
}
