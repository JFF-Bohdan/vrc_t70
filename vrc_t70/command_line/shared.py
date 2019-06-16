import sys

from loguru import logger


def init_logger(log_level="INFO"):
    logger.remove()

    logger.add(
        sys.stderr,
        format="{time:YYYY-MM-DD at HH:mm:ss} | {level} {message}",
        level=log_level,
        backtrace=True,
        diagnose=True
    )

    return logger
