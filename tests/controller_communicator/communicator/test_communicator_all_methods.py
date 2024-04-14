import math
from unittest import mock

from tests.support import common_packets
from tests.support import fake_serial

from vrc_t70 import controller_communicator
from vrc_t70.protocol import responses


def test_can_create_communicator():
    port = fake_serial.FakeSerial()
    _ = controller_communicator.VrcT70Communicator(port=port)

    assert port.written_data == []


def test_can_ping():
    port = fake_serial.FakeSerial(responses=common_packets.PING_RESPONSE)
    comm = controller_communicator.VrcT70Communicator(port=port, address=0x08, sequence_id=0x2233)
    comm.ping()
    assert port.written_data == [common_packets.PING_REQUEST]


def test_can_get_session_id_request():
    port = fake_serial.FakeSerial(responses=common_packets.GET_SESSION_ID_RESPONSE)
    comm = controller_communicator.VrcT70Communicator(port=port, address=0x08, sequence_id=0x2233)

    session_id = comm.get_session_id()
    assert session_id == 0xdeadbeef
    assert port.written_data == [common_packets.GET_SESSION_ID_REQUEST]


@mock.patch("vrc_t70.controller_communicator.base_communicator.time.sleep")
def test_can_get_and_set_different_session_id(_mocked_sleep):
    # Sequence id 0x2234, Session id 0xcafebabe
    SET_SESSION_ID_REQUEST_V2 = bytes([0x08, 0x06, 0x22, 0x34, 0x04, 0xca, 0xfe, 0xba, 0xbe, 0x8f])
    SET_SESSION_ID_RESPONSE_V2 = bytes([0x08, 0x06, 0x22, 0x34, 0x00, 0x04, 0xca, 0xfe, 0xba, 0xbe, 0x0e])

    GET_SESSION_ID_REQUEST_V2 = bytes([0x08, 0x07, 0x22, 0x35, 0x00, 0x56])
    # Sequence id 0x2235, session id 0xcafebabe
    GET_SESSION_ID_RESPONSE_V2 = bytes([0x08, 0x07, 0x22, 0x35, 0x00, 0x04, 0xca, 0xfe, 0xba, 0xbe, 0xad])

    port = fake_serial.FakeSerial(
        responses=common_packets.GET_SESSION_ID_RESPONSE + SET_SESSION_ID_RESPONSE_V2 + GET_SESSION_ID_RESPONSE_V2

    )
    comm = controller_communicator.VrcT70Communicator(port=port, address=0x08, sequence_id=0x2233)

    session_id = comm.get_session_id()
    assert session_id == 0xdeadbeef

    response_session_id = comm.set_session_id(session_id=0xcafebabe)
    assert response_session_id == 0xcafebabe

    session_id = comm.get_session_id()
    assert session_id == 0xcafebabe

    assert port.written_data == [
        common_packets.GET_SESSION_ID_REQUEST,
        SET_SESSION_ID_REQUEST_V2,
        GET_SESSION_ID_REQUEST_V2
    ]


def test_can_rescan_sensors_on_trunk():
    port = fake_serial.FakeSerial(responses=common_packets.RESCAN_SENSORS_ON_TRUNK_RESPONSE)
    comm = controller_communicator.VrcT70Communicator(port=port, address=0x08, sequence_id=0x2233)

    sensors_count = comm.rescan_sensors_on_trunk(trunk_number=4)
    assert sensors_count == 3
    assert port.written_data == [common_packets.RESCAN_SENSORS_ON_TRUNK_REQUEST]


def test_get_get_sensors_count_on_trunk():
    port = fake_serial.FakeSerial(responses=common_packets.GET_SENSORS_COUNT_ON_TRUNK_RESPONSE)
    comm = controller_communicator.VrcT70Communicator(port=port, address=0x08, sequence_id=0x2233)
    comm.get_get_sensors_count_on_trunk(trunk_number=4)
    assert port.written_data == [common_packets.GET_SENSORS_COUNT_ON_TRUNK_REQUEST]


def test_get_temperature_of_sensor_on_trunk():
    port = fake_serial.FakeSerial(responses=common_packets.GET_TEMPERATURE_OF_SENSOR_ON_TRUNK_RESPONSE)
    comm = controller_communicator.VrcT70Communicator(port=port, address=0x08, sequence_id=0x2233)

    temperature = comm.get_temperature_of_sensor_on_trunk(trunk_number=4, sensor_index=5)

    assert math.isclose(temperature, 19.98, abs_tol=0.01)
    assert port.written_data == [common_packets.GET_TEMPERATURE_OF_SENSOR_ON_TRUNK_REQUEST]


def test_get_temperature_of_sensors_on_trunk():
    port = fake_serial.FakeSerial(responses=common_packets.GET_TEMPERATURES_ON_TRUNK_RESPONSE_5_SENSORS)
    comm = controller_communicator.VrcT70Communicator(port=port, address=0x08, sequence_id=0x2233)

    sensors_info = comm.get_temperature_of_sensors_on_trunk(trunk_number=4)

    is_connected = [sensor.is_connected for sensor in sensors_info]
    expected_is_connected = [True, True, True, False, True]
    assert is_connected == expected_is_connected

    temperatures = [sensor.temperature for sensor in sensors_info]
    expected_temperatures = [19.9792, 20.94, 18.44, None, 19.62]
    for index, expected in enumerate(expected_temperatures):
        if expected is None:
            assert temperatures[index] is None
            continue

        assert math.isclose(temperatures[index], expected, abs_tol=0.01)

    assert port.written_data == [common_packets.GET_TEMPERATURES_ON_TRUNK_REQUEST]


def test_get_sensor_unique_address_on_trunk():
    port = fake_serial.FakeSerial(responses=common_packets.GET_SENSOR_UNIQUE_ADDRESS_ON_TRUNK_RESPONSE)
    comm = controller_communicator.VrcT70Communicator(port=port, address=0x08, sequence_id=0x2233)

    sensor_address = comm.get_sensor_unique_address_on_trunk(trunk_number=4, sensor_index=5)
    assert sensor_address == 0x28ff2c7d901501c1

    assert port.written_data == [common_packets.GET_SENSOR_UNIQUE_ADDRESS_ON_TRUNK_REQUEST]


def test_get_sensors_unique_address_on_trunk():
    port = fake_serial.FakeSerial(responses=common_packets.GET_SENSORS_UNIQUE_ADDRESS_ON_TRUNK_RESPONSE_10_SENSORS)
    comm = controller_communicator.VrcT70Communicator(port=port, address=0x08, sequence_id=0x2233)
    expected_response = [
        responses.data_types.SensorAddressInfo(
            trunk_number=4,
            sensor_index=0,
            is_error_detected=False,
            address=0x54000001f15c5728,
        ),
        responses.data_types.SensorAddressInfo(
            trunk_number=4,
            sensor_index=1,
            is_error_detected=True,
            address=0xf8031674dc8aff28,
        ),
        responses.data_types.SensorAddressInfo(
            trunk_number=4,
            sensor_index=2,
            is_error_detected=False,
            address=0x66041674b616ff28,
        ),
        responses.data_types.SensorAddressInfo(
            trunk_number=4,
            sensor_index=3,
            is_error_detected=True,
            address=0xf5031674e23eff28,
        ),
        responses.data_types.SensorAddressInfo(
            trunk_number=4,
            sensor_index=4,
            is_error_detected=False,
            address=0x9f0416805499ff28,
        ),
        responses.data_types.SensorAddressInfo(
            trunk_number=4,
            sensor_index=5,
            is_error_detected=False,
            address=0x87031674b483ff28,
        ),
        responses.data_types.SensorAddressInfo(
            trunk_number=4,
            sensor_index=6,
            is_error_detected=True,
            address=0x2818b4490c00007c,
        ),
        responses.data_types.SensorAddressInfo(
            trunk_number=4,
            sensor_index=7,
            is_error_detected=True,
            address=0x28cc19490c0000bb,
        ),
        responses.data_types.SensorAddressInfo(
            trunk_number=4,
            sensor_index=8,
            is_error_detected=True,
            address=0x2819ef480c000021,
        ),
        responses.data_types.SensorAddressInfo(
            trunk_number=4,
            sensor_index=9,
            is_error_detected=False,
            address=0x28c6de49f6b63c55,
        ),
    ]
    sensors_address = comm.get_sensors_unique_address_on_trunk(trunk_number=4)
    assert sensors_address == expected_response
    assert port.written_data == [common_packets.GET_SENSORS_UNIQUE_ADDRESS_ON_TRUNK_REQUEST]


def test_set_controller_new_address():
    port = fake_serial.FakeSerial(responses=common_packets.SET_CONTROLLER_NEW_ADDRESS_RESPONSE)
    comm = controller_communicator.VrcT70Communicator(port=port, address=0x08, sequence_id=0x2233)

    comm.set_controller_new_address(new_controller_address=42)

    assert port.written_data == [common_packets.SET_CONTROLLER_NEW_ADDRESS_REQUEST]
    # Should adjust address to a new one
    assert comm.address == 42
