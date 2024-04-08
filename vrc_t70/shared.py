import dataclasses
import datetime
import struct
import time
import typing

import serial

from vrc_t70 import limitations


@dataclasses.dataclass
class FullSensorInfo:
    trunk_number: int
    sensor_index: int
    address: int
    # is_connected: bool = False
    has_error: bool = False
    temperature: typing.Optional[float | None] = None


def init_serial(port_name: str, baudrate: int, timeout: float):
    return serial.Serial(
        port_name,
        baudrate=baudrate,
        bytesize=serial.EIGHTBITS,
        timeout=timeout,
        parity=serial.PARITY_NONE,
        stopbits=serial.STOPBITS_ONE
    )


def timedelta_from_monotonic_time(timestamp_begin: float) -> datetime.timedelta:
    return datetime.timedelta(seconds=float(time.monotonic() - timestamp_begin))


def default_wait_time_for_symbol(port_speed: int) -> float:
    """
    Returns default wait time for transmission of symbol
    """
    return 1.5 * (1.0 / port_speed)


def decode_float(data: bytes) -> float:
    """
    Decodes 32 bits float from 4 bytes representing float in big endian
    """
    return struct.unpack("<f", data)


def trunks_indexes() -> typing.Generator[int, None, None]:
    """
    Helper that returns generator for trunks numbers.

    Instead of

    ```
    for trunk_number in range(limitations.MIN_TRUNK_NUMBER, limitations.MAX_TRUNK_NUMBER + 1):
        pass
    ```

    You can just use:

    ```
    for trunk_number in trunks_indexes():
        pass
    ```

    """
    return range(limitations.MIN_TRUNK_NUMBER, limitations.MAX_TRUNK_NUMBER + 1)


def list_of_nones_for_trunk() -> list:
    return [None] * (limitations.MAX_SENSOR_INDEX + 1)
