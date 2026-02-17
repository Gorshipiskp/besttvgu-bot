from typing import Final

from pydantic import ConfigDict
from pydantic_settings import BaseSettings


class BotSettings(BaseSettings):
    bot_token: str
    api_url: str
    bot_api_token: str
    creator_telegram_id: int
    api_request_timeout: int

    model_config = ConfigDict(
        env_file=".env"
    )


bot_settings: BotSettings = BotSettings()


# Показывать ли тайминги middlewares в консоле
SHOW_MIDDLEWARES_PERFORMANCE: Final[bool] = False

# Да, много, но мы рассчитываем на корректную инвалидацию
USER_CACHE_TTL_SECONDS: Final[int] = 3600 * 24 * 7

MESSAGES_TEMPLATES_DIR: Final[str] = "messages_templates"
TELEGRAM_CHANNEL_LINK: Final[str] = "https://t.me/best_tvgu"
WEBSITE_URL: Final[str] = "https://besttvgu.ru/"
