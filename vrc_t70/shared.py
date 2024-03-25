import datetime
import struct
import time

import serial


def init_serial(uart_name, uart_speed, wait_delay):
    return serial.Serial(
        uart_name,
        baudrate=uart_speed,
        bytesize=serial.EIGHTBITS,
        timeout=wait_delay,
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
