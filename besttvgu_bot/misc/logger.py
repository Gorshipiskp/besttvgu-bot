import os
from logging import Logger, getLogger, INFO, Formatter
from logging.handlers import TimedRotatingFileHandler

from besttvgu_bot.consts import LEVELS_TO_LOG


def init_logger(name="besttvgu_bot", log_dir="logs") -> Logger:
    os.makedirs(log_dir, exist_ok=True)

    logger: Logger = getLogger(name)
    logger.setLevel(INFO)

    formatter: Formatter = Formatter('%(asctime)s | %(levelname)s | %(name)s | %(message)s')

    handlers_to_add: list[TimedRotatingFileHandler] = []

    for level, level_name in LEVELS_TO_LOG.items():
        new_handler: TimedRotatingFileHandler = TimedRotatingFileHandler(
            f"{log_dir}/app_{level_name}.log", when="midnight", interval=1, backupCount=7
        )
        new_handler.setLevel(level)
        new_handler.setFormatter(formatter)

        handlers_to_add.append(new_handler)

    if not logger.hasHandlers():
        for handler in handlers_to_add:
            logger.addHandler(handler)

    logger.info("Logger initialized")

    return logger


logger: Logger = init_logger()
