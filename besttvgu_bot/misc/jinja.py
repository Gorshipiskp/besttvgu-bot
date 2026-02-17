from enum import Enum
from pathlib import Path

from aiogram.methods import SendMessage
from aiogram.types import Message, Update
from jinja2 import Environment, FileSystemLoader, select_autoescape, StrictUndefined, Template

from besttvgu_bot.config import MESSAGES_TEMPLATES_DIR
from besttvgu_bot.misc.misc import safe_answer

BASE_DIR: Path = Path(__file__).parent.parent

jinja_env: Environment = Environment(
    loader=FileSystemLoader(BASE_DIR / MESSAGES_TEMPLATES_DIR),
    autoescape=select_autoescape(
        enabled_extensions=("html", "xml")
    ),
    undefined=StrictUndefined,
    enable_async=False,
    trim_blocks=True,
    lstrip_blocks=True
)


def render_template(template_name: str, **context) -> str:
    if isinstance(template_name, Enum):
        template_name = template_name.value

    template: Template = jinja_env.get_template(template_name)
    return template.render(**context)


async def answer_by_template(
        message: Message | Update,
        template_name: str,
        template_params: dict[str, str] | None = None,
        **kwargs
) -> SendMessage:
    """
    Функция отправки ответа текстовым сообщением с использованием шаблона.
    Приоритетно используем эту функцию

    Args:
        message: Сообщение для ответа (`Message`)
        template_name: Имя шаблона
        template_params: Параметры подстановки
        kwargs: Опциональные аргументы

    Returns:
        Экземпляр отправленного сообщения (`SendMessage`)
    """

    if template_params is None:
        template_params = {}

    template_rendered: str = render_template(template_name, **template_params)

    return await safe_answer(
        message=message,
        text=template_rendered,
        **kwargs
    )
