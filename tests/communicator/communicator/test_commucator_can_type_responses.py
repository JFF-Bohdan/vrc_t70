import pytest

from tests.support import common_packets
from tests.support import ex_time_machine
from tests.support import fake_serial

from vrc_t70 import controller_communicator, exceptions
from vrc_t70.protocol.requests import request_codes


TEST_CASES = [
    # structure of test case:
    #
    # - response [if not specified, will use ping response],
    # - expected request which should be sent,
    # - lambda to initiate communication
    (
        common_packets.GET_SESSION_ID_RESPONSE,
        [common_packets.PING_REQUEST],
        lambda comm: comm.ping()
    ),
    (
        None,
        [common_packets.GET_SESSION_ID_REQUEST],
        lambda comm: comm.get_session_id()
    ),
    (
        None,
        [common_packets.SET_SESSION_ID_REQUEST],
        lambda comm: comm.set_session_id(session_id=0xdeadbeef)
    ),

    (
        None,
        [common_packets.RESCAN_SENSORS_ON_TRUNK_REQUEST],
        lambda comm: comm.rescan_sensors_on_trunk(trunk_number=4)
    ),

    (
        None,
        [common_packets.GET_SENSORS_COUNT_ON_TRUNK_REQUEST],
        lambda comm: comm.get_get_sensors_count_on_trunk(trunk_number=4)
    ),

    (
        None,
        [common_packets.GET_TEMPERATURE_OF_SENSOR_ON_TRUNK_REQUEST],
        lambda comm: comm.get_temperature_of_sensor_on_trunk(trunk_number=4, sensor_index=5)
    ),

    (
        None,
        [common_packets.GET_SENSOR_UNIQUE_ADDRESS_ON_TRUNK_REQUEST],
        lambda comm: comm.get_sensor_unique_address_on_trunk(trunk_number=4, sensor_index=5)
    ),

    (
        None,
        [common_packets.GET_SENSORS_UNIQUE_ADDRESS_ON_TRUNK_REQUEST],
        lambda comm: comm.get_sensors_unique_address_on_trunk(trunk_number=4)
    ),

    (
        None,
        [common_packets.SET_CONTROLLER_NEW_ADDRESS_REQUEST],
        lambda comm: comm.set_controller_new_address(new_controller_address=42)
    ),

    (
        None,
        [common_packets.GET_TEMPERATURES_ON_TRUNK_REQUEST],
        lambda comm: comm.get_temperature_of_sensors_on_trunk(trunk_number=4)
    ),

]


@ex_time_machine.travel(123000, tick_delta=0.01)
def test_for_response_types_validation():
    """
    Testing that responses would have expected data type. In this test we would simulate when for each and
    every request we would receive unexpected response from controller.
    """

    def extract_request_id(raw_packet: bytes) -> int:
        return raw_packet[1]

    # Confirming that we have test cases for all available commands
    available_test_cases_requests = [extract_request_id(case[1][0]) for case in TEST_CASES]
    assert set(available_test_cases_requests) == set(request_codes.RequestCodes.all_known_codes())

    for wrong_packet, expected_communication, sender in TEST_CASES:
        wrong_packet = wrong_packet if wrong_packet else common_packets.PING_RESPONSE
        port = fake_serial.FakeSerial(responses=wrong_packet)
        comm = controller_communicator.VrcT70Communicator(port=port, address=0x08, sequence_id=0x2233)
        with pytest.raises(exceptions.ErrorUnknownResponse):
            sender(comm)

        assert port.written_data == expected_communication
