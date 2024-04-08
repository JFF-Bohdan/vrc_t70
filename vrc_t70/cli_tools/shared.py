import functools
import logging
import logging.config
import pkgutil
import signal
import threading
import typing

import yaml

logger = logging.getLogger(__name__)


def signal_handler(message: str, stop_event: threading.Event, signum, frame):
    """
    Signal handler, used to notify that some event occurred. Used to intercept event
    when Ctrl-C pressed to signal application to stop.

    Once signal received it would write log message and set instance of threading.Event
    """

    logger.warning(message)
    stop_event.set()


def create_handler(message: str, event: threading.Event) -> typing.Callable:
    """
    Can be used to create partial function from signal_handler by providing values of message
    that need to be printed and event to be set.

    Result of this function then can be used for signal.signal()
    """
    return functools.partial(signal_handler, message, event)


def register_interception_of_ctrl_c(message: str, event: threading.Event) -> None:
    """
    Registers interceptor for Ctrl-C
    """
    func = create_handler(message, event)
    signal.signal(signal.SIGINT, func)


def setup_logging():
    data = pkgutil.get_data("vrc_t70", "data/log_config.yaml")
    config = yaml.safe_load(data)
    logging.config.dictConfig(config)
