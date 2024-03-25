import dataclasses
import typing


@dataclasses.dataclass(frozen=True)
class SensorTemperatureInfo:
    trunk_number: int
    sensor_index: int
    is_connected: bool
    temperature: typing.Optional[float]


@dataclasses.dataclass(frozen=True)
class SensorAddressInfo:
    trunk_number: int
    sensor_index: int
    is_error_detected: bool
    address: int
