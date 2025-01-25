import logging
from logging import Logger

from colorama import Fore, Style

LOGGING_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
LOGGING_DATE_FORMAT = "%H:%M:%S"


class ColoredFormatter(logging.Formatter):
    COLORS = {
        "DEBUG": Fore.CYAN,
        "INFO": Fore.GREEN,
        "WARNING": Fore.YELLOW,
        "ERROR": Fore.RED,
        "CRITICAL": Fore.MAGENTA,
    }

    def format(self, record):
        msg = super().format(record)
        color = self.COLORS.get(record.levelname, "")

        return f"{color}{msg}{Style.RESET_ALL}"


def get_colored_logger(name: str, level: int = logging.INFO, log_file: str = None) -> Logger:
    logger = logging.getLogger(name)
    logger.setLevel(level)

    formatter = ColoredFormatter(
        fmt=LOGGING_FORMAT,
        datefmt=LOGGING_DATE_FORMAT
    )

    handler = logging.StreamHandler()
    handler.setLevel(level)
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    if log_file:
        file_handler = logging.FileHandler(log_file, mode='w')
        file_handler.setLevel(level)
        file_formatter = logging.Formatter(fmt=LOGGING_FORMAT, datefmt=LOGGING_DATE_FORMAT)
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)

    return logger
