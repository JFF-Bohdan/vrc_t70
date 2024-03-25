import pytest

from vrc_t70 import exceptions
from vrc_t70 import limitations


@pytest.mark.parametrize(
    "value",
    [
        0x00,
        limitations.MAX_CONTROLLER_ADDRESS + 1,
        limitations.MAX_CONTROLLER_ADDRESS + 2
    ]
)
def test_throws_error_for_wrong_controller_addresses(value):
    with pytest.raises(exceptions.ErrorValueError):
        limitations.validate_controller_address(value)


@pytest.mark.parametrize(
    "value",
    [
        limitations.MIN_CONTROLLER_ADDRESS,
        limitations.MIN_CONTROLLER_ADDRESS + 1,
        limitations.MAX_CONTROLLER_ADDRESS - 2,
        limitations.MAX_CONTROLLER_ADDRESS - 1,
        limitations.MAX_CONTROLLER_ADDRESS
    ]
)
def test_accept_valid_addresses(value):
    limitations.validate_controller_address(value)


@pytest.mark.parametrize(
    "value",
    [
        limitations.MIN_TRUNK_NUMBER - 2,
        limitations.MIN_TRUNK_NUMBER - 1,
        limitations.MAX_TRUNK_NUMBER + 1,
        limitations.MAX_TRUNK_NUMBER + 2
    ]
)
def test_throws_error_on_wrong_trunk_number(value):
    with pytest.raises(exceptions.ErrorValueError):
        limitations.validate_trunk_number(value)


@pytest.mark.parametrize(
    "value",
    [
        limitations.MIN_TRUNK_NUMBER,
        limitations.MAX_TRUNK_NUMBER - 2,
        limitations.MAX_TRUNK_NUMBER - 1,
        limitations.MAX_TRUNK_NUMBER
    ]
)
def test_accepts_valid_trunk_number(value):
    limitations.validate_trunk_number(value)


@pytest.mark.parametrize(
    "value",
    [
        limitations.MIN_SENSOR_INDEX - 1,
        limitations.MAX_SENSOR_INDEX + 1,
        limitations.MAX_SENSOR_INDEX + 2
    ]
)
def test_throws_error_on_wrong_sensor_index(value):
    with pytest.raises(exceptions.ErrorValueError):
        limitations.validate_sensor_index(value)


@pytest.mark.parametrize(
    "value",
    [
        limitations.MIN_SENSOR_INDEX,
        limitations.MIN_SENSOR_INDEX + 1,
        limitations.MAX_SENSOR_INDEX - 2,
        limitations.MAX_SENSOR_INDEX - 1,
        limitations.MAX_SENSOR_INDEX
    ]
)
def test_accepts_valid_sensor_index(value):
    limitations.validate_sensor_index(value)


@pytest.mark.parametrize("value", [2, 42, 0xff, 0x100, 0x101])
def test_throws_error_on_wrong_bool_value(value):
    with pytest.raises(exceptions.ErrorValueError):
        limitations.validate_bool(value)


@pytest.mark.parametrize("value", [0, 1])
def test_accepts_valid_bool_value(value):
    limitations.validate_bool(value)


@pytest.mark.parametrize(
    "address",
    [
        limitations.MIN_SEQUENCE_ID - 2,
        limitations.MIN_SEQUENCE_ID - 1,
        limitations.MAX_SEQUENCE_ID + 1,
        limitations.MAX_SEQUENCE_ID + 2,
    ]
)
def test_throws_error_on_wrong_sequence_id(address):
    with pytest.raises(exceptions.ErrorValueError):
        limitations.validate_sequence_id(address)


@pytest.mark.parametrize(
    "address",
    [
        limitations.MIN_SEQUENCE_ID,
        limitations.MIN_SEQUENCE_ID + 1,
        limitations.MIN_SEQUENCE_ID + 2,
        limitations.MAX_SEQUENCE_ID - 2,
        limitations.MAX_SEQUENCE_ID - 1,
    ]
)
def test_accepts_correct_sequence_id(address):
    limitations.validate_sequence_id(address)
