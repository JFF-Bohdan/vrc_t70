from vrc_t70 import exceptions

MIN_CONTROLLER_ADDRESS = 0x01
MAX_CONTROLLER_ADDRESS = 0xff - 1

MIN_TRUNK_NUMBER = 1
MAX_TRUNK_NUMBER = 7

MIN_SENSOR_INDEX = 0
MAX_SENSOR_INDEX = 9

MAX_SESSION_ID = 0xffffffff - 1

MIN_SEQUENCE_ID = 0x0000
MAX_SEQUENCE_ID = 0xffff


def validate_controller_address(address: int, prefix: str = "Invalid controller address, "):
    if (address < MIN_CONTROLLER_ADDRESS) or (address > MAX_CONTROLLER_ADDRESS):
        raise exceptions.ErrorValueError(
            f"{prefix}can be from {MIN_CONTROLLER_ADDRESS} to {MAX_CONTROLLER_ADDRESS}"
        )


def validate_trunk_number(trunk_number: int) -> None:
    if (trunk_number < MIN_TRUNK_NUMBER) or (trunk_number > MAX_TRUNK_NUMBER):
        raise exceptions.ErrorValueError(f"Trunk number should be between {MIN_TRUNK_NUMBER} and {MAX_TRUNK_NUMBER}")


def validate_sensor_index(sensor_index: int) -> None:
    if (sensor_index < MIN_SENSOR_INDEX) or (sensor_index > MAX_SENSOR_INDEX):
        raise exceptions.ErrorValueError(
            f"Sensor index should be between {MIN_SENSOR_INDEX} and {MAX_SENSOR_INDEX}"
        )


def validate_bool(value: int):
    if value not in (0, 1):
        raise exceptions.ErrorValueError(
            f"Unexpected bool value, should be 0 or 1. Got {value} instead"
        )


def validate_sequence_id(sequence_id):
    if (sequence_id < 0) or (sequence_id > 0xffff):
        raise exceptions.ErrorValueError(
            f"Incorrect value for sequence id. Allowed values from 0x{MIN_SEQUENCE_ID:04x} to {MAX_SEQUENCE_ID:04x}"
        )
