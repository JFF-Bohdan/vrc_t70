import itertools

import pytest

from tests.support import fake_serial

from vrc_t70 import exceptions
from vrc_t70 import limitations
from vrc_t70.communicator import communicator


COMMUNICATIONS_TO_TEST_TRUNKS_ONLY = [
    (
        lambda comm, trunk, _: comm.rescan_sensors_on_trunk(trunk_number=trunk)
    ),
    (
        lambda comm, trunk, _: comm.get_get_sensors_count_on_trunk(trunk_number=trunk)
    ),
    (
        lambda comm, trunk, _: comm.get_temperature_of_sensors_on_trunk(trunk_number=trunk)
    ),
    (
        lambda comm, trunk, _: comm.get_sensors_unique_address_on_trunk(trunk_number=trunk)
    ),
]

COMMUNICATIONS_TO_TEST_TRUNKS_AND_SENSOR_INDEX = [
    (
        lambda comm, trunk, sensor: comm.get_temperature_of_sensor_on_trunk(
            trunk_number=trunk,
            sensor_index=sensor
        )
    ),

    (
        lambda comm, trunk, sensor: comm.get_sensor_unique_address_on_trunk(
            trunk_number=trunk,
            sensor_index=sensor
        )
    ),
]


@pytest.mark.parametrize(
    "trunk",
    [limitations.MIN_TRUNK_NUMBER - 1, limitations.MAX_TRUNK_NUMBER + 1, limitations.MAX_TRUNK_NUMBER + 2]
)
@pytest.mark.parametrize(
    "sensor",
    [limitations.MIN_SENSOR_INDEX, limitations.MAX_SENSOR_INDEX, limitations.MAX_SENSOR_INDEX - 1]
)
def test_for_bad_trunks_and_good_sensors(trunk, sensor):
    for case in itertools.chain(COMMUNICATIONS_TO_TEST_TRUNKS_ONLY, COMMUNICATIONS_TO_TEST_TRUNKS_AND_SENSOR_INDEX):
        port = fake_serial.FakeSerial(responses=[])
        comm = communicator.VrcT70Communicator(port=port, address=0x08, sequence_id=0x2233)
        with pytest.raises(exceptions.ErrorValueError):
            case(comm, trunk, sensor)


@pytest.mark.parametrize(
    "trunk",
    [limitations.MIN_TRUNK_NUMBER, limitations.MAX_TRUNK_NUMBER - 1, limitations.MAX_TRUNK_NUMBER]
)
@pytest.mark.parametrize(
    "sensor",
    [limitations.MIN_SENSOR_INDEX - 1, limitations.MAX_SENSOR_INDEX + 1, limitations.MAX_SENSOR_INDEX + 2]
)
def test_for_good_trunks_and_bad_sensors(trunk, sensor):
    for case in COMMUNICATIONS_TO_TEST_TRUNKS_AND_SENSOR_INDEX:
        port = fake_serial.FakeSerial(responses=[])
        comm = communicator.VrcT70Communicator(port=port, address=0x08, sequence_id=0x2233)
        with pytest.raises(exceptions.ErrorValueError):
            case(comm, trunk, sensor)


@pytest.mark.parametrize(
    "session_id",
    [limitations.MAX_SESSION_ID + 1, limitations.MAX_SESSION_ID + 2, 0]
)
def test_for_session_id(session_id):
    port = fake_serial.FakeSerial(responses=[])
    comm = communicator.VrcT70Communicator(port=port, address=0x08, sequence_id=0x2233)
    with pytest.raises(exceptions.ErrorValueError):
        comm.set_session_id(session_id=session_id)


@pytest.mark.parametrize(
    "new_address",
    [0, limitations.MAX_CONTROLLER_ADDRESS + 1, limitations.MAX_CONTROLLER_ADDRESS + 2, 0]
)
def test_for_controller_address(new_address):
    port = fake_serial.FakeSerial(responses=[])
    comm = communicator.VrcT70Communicator(port=port, address=0x08, sequence_id=0x2233)
    with pytest.raises(exceptions.ErrorValueError):
        comm.set_controller_new_address(new_controller_address=new_address)
