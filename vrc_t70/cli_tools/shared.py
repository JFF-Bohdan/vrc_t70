import collections
import dataclasses
import functools
import logging
import logging.config
import pkgutil
import signal
import threading
import typing

import terminaltables

from vrc_t70 import shared

import yaml

logger = logging.getLogger(__name__)


@dataclasses.dataclass
class TrunkInfo:
    sensors_count: int = 0
    sensors_addresses: dict[int, int] = dataclasses.field(default_factory=lambda: {})
    sensors_temperatures: dict[int, float] = dataclasses.field(default_factory=lambda: {})


@dataclasses.dataclass
class VrcT70DeviceInfo:
    address: int = 0
    session_id: int = 0
    trunks: dict[int, TrunkInfo] = dataclasses.field(default_factory=lambda: collections.defaultdict(TrunkInfo))


def print_scan_info(info: VrcT70DeviceInfo) -> str:
    header = ["Trunk", "Sensors count", "Sensor index", "Sensor address", "Temperature"]
    table_data = [header]

    for trunk_number in shared.trunks_indexes():
        trunk_info = info.trunks[trunk_number]
        sensors_index = []
        sensors_address = []
        sensors_temperature = []

        for sensor_index in range(trunk_info.sensors_count):
            sensors_index.append(str(sensor_index))

            sensor_address = trunk_info.sensors_addresses.get(sensor_index)
            sensors_address.append(f"{sensor_address:08x}" if sensor_address is not None else "?")

            sensor_temperature = trunk_info.sensors_temperatures.get(sensor_index)
            sensors_temperature.append(f"{sensor_temperature:0.2f}" if sensor_temperature is not None else "?")

        sensors_index = "\n".join(sensors_index) if sensors_index else "N/A"
        sensors_address = "\n".join(sensors_address) if sensors_address else "N/A"
        sensors_temperature = "\n".join(sensors_temperature) if sensors_temperature else "N/A"
        table_data.append(
            [
                trunk_number,
                trunk_info.sensors_count,
                sensors_index,
                sensors_address,
                sensors_temperature,
            ]
        )

    table = terminaltables.AsciiTable(table_data=table_data)
    return table.table


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
