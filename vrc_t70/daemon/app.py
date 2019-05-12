import signal
import sys
from functools import partial

from loguru import logger as initial_logger

import serial

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from vrc_t70.sample_shared.models.devices import VrcT70Device  # noqa
from vrc_t70.sample_shared.models.sensors import VrcT70Sensor  # noqa
from vrc_t70.sample_shared.models.shared import Base
from vrc_t70.sample_shared.support.config_helper import ConfigHelper
from vrc_t70.sample_shared.support.config_support import get_config

from .vrc_t70_daemon import VrcT70Daemon


def initialize_database(connection_uri, echo=False):
    engine = create_engine(connection_uri, echo=echo)
    return engine


def init_logger(config):
    initial_logger.remove()

    log_format = "{time:YYYY-MM-DD at HH:mm:ss} {level} {file}:{line} {function}() : {message}"

    initial_logger.add(
        sys.stderr,
        format=log_format,
        level=ConfigHelper.get_daemon_log_level(config),
        backtrace=ConfigHelper.get_daemon_log_backtrace(config),
        diagnose=ConfigHelper.get_daemon_log_diagnose(config)
    )

    log_file_name = ConfigHelper.get_daemon_log_file_name(config)
    if log_file_name:
        initial_logger.add(
            log_file_name,
            format=log_format,
            level=ConfigHelper.get_daemon_log_level(config),
            rotation=ConfigHelper.get_daemon_log_file_rotation(config),
            compression=ConfigHelper.get_daemon_log_file_compression(config),
            backtrace=ConfigHelper.get_daemon_log_backtrace(config),
            diagnose=ConfigHelper.get_daemon_log_diagnose(config)
        )

    return initial_logger


def init_serial(uart_name, uart_speed):
    return serial.Serial(
        uart_name,
        baudrate=uart_speed,
        bytesize=serial.EIGHTBITS,
        timeout=1,
        parity=serial.PARITY_NONE,
        stopbits=serial.STOPBITS_ONE
    )


def signal_handler(sig, frame, daemon, logger):
    if not daemon:
        sys.exit(0)

    logger.warning("going to shutdown with Ctrl-C")
    daemon.stop()


def main():
    config = get_config()
    if not config:
        initial_logger.error("can't initialize, can't read config file")
        return -1

    logger = init_logger(config)

    logger.info("daemon started")

    db_uri = ConfigHelper.get_database_connection_uri(config)
    logger.debug("db_uri: '{}'".format(db_uri))

    logger.info("initializing database connection")
    engine = initialize_database(db_uri)

    logger.info("recreating all tables (if required)")
    Base.metadata.create_all(engine)

    Session = sessionmaker(bind=engine)
    session = Session()

    # TODO: load from config
    uart = init_serial("COM15", 115200)
    devices_addresses = [0x01]

    daemon = VrcT70Daemon(uart, devices_addresses, logger, session)

    partial_handler = partial(signal_handler, daemon=daemon, logger=logger)
    signal.signal(signal.SIGINT, partial_handler)

    daemon.init()
    daemon.run()

    logger.info("daemon finished")

    return 0


if __name__ == "__main__":
    res = main()
    exit(res)
