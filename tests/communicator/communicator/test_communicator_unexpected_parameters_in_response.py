import pytest

from tests.support import ex_time_machine
from tests.support import fake_serial

from vrc_t70 import exceptions
from vrc_t70.communicator import communicator


TEST_CASES = [
    # structure of test case:
    #
    # - lambda to initiate communication
    # - response with unexpected information
    (
        # Trying to set session id as 0xcafebabe but receiving that 0xdeadbeef was set
        lambda comm: comm.set_session_id(session_id=0xcafebabe),
        bytes([0x08, 0x06, 0x22, 0x33, 0x00, 0x04, 0xde, 0xca, 0xfb, 0xad, 0x33]),
    ),

    (
        # Scanning trunk 4, but received response from trunk 5
        lambda comm: comm.rescan_sensors_on_trunk(trunk_number=4),
        bytes([0x08, 0x09, 0x22, 0x33, 0x00, 0x02, 0x05, 0x03, 0x11]),
    ),

    (
        # Querying trunk 4, but response from 4
        lambda comm: comm.get_get_sensors_count_on_trunk(trunk_number=4),
        bytes([0x08, 0x0a, 0x22, 0x33, 0x00, 0x02, 0x03, 0x03, 0x42])
    ),

    (
        # Querying trunk 4 / sensor 5, but response from trunk 3 / sensor 5
        lambda comm: comm.get_temperature_of_sensor_on_trunk(trunk_number=4, sensor_index=5),
        bytes(
            [
                0x08,
                0x02,
                0x22, 0x33,
                0x00,
                0x07,
                0x03,
                0x05,
                0x01,
                0x55, 0xd5, 0x9f, 0x41,
                0x9b
            ]
        )
    ),

    (
        # Querying trunk 4 / sensor 5, but response from trunk 3 / sensor 4
        lambda comm: comm.get_temperature_of_sensor_on_trunk(trunk_number=4, sensor_index=5),
        bytes(
            [
                0x08,
                0x02,
                0x22, 0x33,
                0x00,
                0x07,
                0x04,
                0x04,
                0x01,
                0x55, 0xd5, 0x9f, 0x41,
                0x45
            ]
        )
    ),

    (
        # Querying trunk 4, receiving response from trunk 3
        lambda comm: comm.get_temperature_of_sensors_on_trunk(trunk_number=4),

        bytes(
            [
                0x08,
                0x03,
                0x22, 0x33,
                0x00,
                0x06,
                0x03,
                0x01,
                0x00, 0x80, 0xa7, 0x41,
                0x35
            ]
        )
    ),
    (
        # Querying trunk 4 and sensor 5, receiving response from trunk 3 / sensor 5
        lambda comm: comm.get_sensor_unique_address_on_trunk(trunk_number=4, sensor_index=5),

        bytes(
            [
                0x08,
                0x04,
                0x22, 0x33,
                0x00,
                0x0a,
                0x03,
                0x05,
                0x28, 0xff, 0x2c, 0x7d, 0x90, 0x15, 0x01, 0xc1,
                0xca
            ]
        )
    ),
    (
        # Querying trunk 4 and sensor 5, receiving response from trunk 4 / sensor 4
        lambda comm: comm.get_sensor_unique_address_on_trunk(trunk_number=4, sensor_index=5),

        bytes(
            [
                0x08,
                0x04,
                0x22, 0x33,
                0x00,
                0x0a,
                0x04,
                0x04,
                0x28, 0xff, 0x2c, 0x7d, 0x90, 0x15, 0x01, 0xc1,
                0x39
            ]
        )
    ),

    (
        # Querying trunk 4, but received response from trunk 3
        lambda comm: comm.get_sensors_unique_address_on_trunk(trunk_number=4),

        bytes(
            [
                0x08,
                0x05,
                0x22, 0x33,
                0x00,
                0x0a,
                0x03,

                0x28, 0xff, 0x2c, 0x7d, 0x90, 0x15, 0x01, 0xc1,
                0x00,
                0xdf
            ]
        )
    ),

    (
        # Attempting to set 42, but instead got 33
        lambda comm: comm.set_controller_new_address(new_controller_address=42),

        bytes([0x08, 0x08, 0x22, 0x33, 0x00, 0x01, 0x21, 0x58])
    ),
]


@ex_time_machine.travel(123000, tick_delta=0.01)
def test_raises_exception_on_unknown_response():
    """
    Testing that communicator will raise exception if we would have valida packet (valid structure and CRC)
    with unexpected parameters
    """

    for sender, response in TEST_CASES:
        port = fake_serial.FakeSerial(responses=response)
        comm = communicator.VrcT70Communicator(port=port, address=0x08, sequence_id=0x2233)
        with pytest.raises(exceptions.ErrorUnknownResponse):
            sender(comm)
