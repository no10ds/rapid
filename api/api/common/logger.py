import logging
from typing import Any


def init_logger():
    logging.basicConfig(format="%(levelname)s: %(message)s", level=logging.INFO)


class AppLogger:
    _logger = logging.getLogger("rapid_logger")

    @staticmethod
    def warning(msg: str, *args: Any):
        AppLogger._logger.warning(msg, *args, exc_info=True)

    @staticmethod
    def error(msg: str, *args: Any):
        AppLogger._logger.error(msg, *args, exc_info=True)

    @staticmethod
    def info(msg: str, *args: Any):
        AppLogger._logger.info(msg, *args)
