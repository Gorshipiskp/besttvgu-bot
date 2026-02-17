from typing import Final, TypeVar

from httpx import Headers, URL, AsyncClient
from httpx import Response
from pydantic import BaseModel, ValidationError

from besttvgu_bot.config import bot_settings

CUR_ENDPOINT_PREFIX: Final[URL] = URL(bot_settings.api_url)

T = TypeVar("T", BaseModel, None)


# todo: Сделать синглтон для AsyncClient

def get_headers() -> Headers:
    return Headers(
        headers={
            "Authorization": f"Bearer {bot_settings.bot_api_token}",
            "Content-Type": "application/json"
        }
    )


async def api_get(endpoint: str, model: T = None) -> T | dict:
    """
    Асинхронный GET-запрос и валидация ответа в модель Pydantic v2

    Args:
        endpoint: URL эндпоинта для запроса (он прилепляется к общему API URL, указанном в `.env`)
        model: Класс модели Pydantic

    Returns:
        Валидированный объект модели, либо сырой dict

    Raises:
        HTTPStatusError: если HTTP статус != 2xx
        pydantic.ValidationError: если JSON не соответствует модели
    """

    async with AsyncClient(
            timeout=bot_settings.api_request_timeout
    ) as client:
        response: Response = await client.get(
            url=CUR_ENDPOINT_PREFIX.join(endpoint),
            headers=get_headers()
        )
        response.raise_for_status()

        data: object = response.json()
        if model is None:
            return data

        try:
            return model.model_validate(data)
        except ValidationError as e:
            # не должно быть такого, если с бэкендом всё ок (проблема либо в бэке, либо в некорректной модели)
            raise e


async def api_post(
        url: URL | str,
        post_data: object | BaseModel,
        model: T = None
) -> T | dict:
    """
    Асинхронный POST-запрос и валидация ответа в модель Pydantic v2

    Args:
        url: URL эндпоинта для запроса (он прилепляется к общему API URL, указанном в `.env`)
        post_data: Данные для POST-запроса
        model: Класс модели Pydantic

    Returns:
        Валидированный объект модели, либо сырой dict

    Raises:
        HTTPStatusError: если HTTP статус != 2xx
        pydantic.ValidationError: если JSON не соответствует модели
    """

    async with AsyncClient(
            timeout=bot_settings.api_request_timeout
    ) as client:
        response: Response = await client.post(
            url=CUR_ENDPOINT_PREFIX.join(url),
            json=post_data.model_dump() if isinstance(post_data, BaseModel) else post_data,
            headers=get_headers()
        )
        response.raise_for_status()

        data: object = response.json()
        if model is None:
            return data

        try:
            return model.model_validate(data)
        except ValidationError as e:
            # не должно быть такого, если с бэкендом всё ок (проблема либо в бэке, либо в некорректной модели)
            raise e
