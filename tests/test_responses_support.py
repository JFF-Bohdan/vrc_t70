import binascii
import struct

from vrc_t70.core.limitations import MAX_SENSORS_PER_TRUNK
from vrc_t70.core.response import ControllerNewAddressResponse, SensorUniqueAddressOnTrunkResponse, SensorUniqueIdResponse, \
    SessionIdResponse, TemperatureOnSensorResponse, TemperatureOnTrunkResponse, TrunkSensortsCountResponse, \
    VrcT70Response

from .shared import bytearray_to_response


def test_response_crc_validation():
    r = VrcT70Response()
    r.address = 0x01
    r.id_event = 0x01
    r.sequence_id = 0xaabb
    r.processing_result = 0x00
    r.crc = 0x74

    assert r.is_crc_valid()


def test_responses_builder_produces_correct_response_with_crc():
    res = bytearray_to_response("0101aabb000074")
    assert res.crc == 0x074


def test_responses_builder_produces_correct_response_without_crc():
    res = bytearray_to_response("0101aabb0000", False)

    assert res.crc == 0x74


def test_response_builder_can_parse_data_segment():
    res = bytearray_to_response("010922330002aabb72")

    res.address = 0x01
    res.id_event = 0x09
    res.sequence_id = 0x2233
    res.processing_result = 0x00

    assert len(res.data) == 2
    assert res.data == bytearray([0xaa, 0xbb])

    assert res.crc == 0x72


def test_sensor_count_response_can_parse_data_segment():
    res = TrunkSensortsCountResponse(bytearray_to_response("010922330002aabb72"))

    assert res.trunk_number() == 0xaa
    assert res.sensors_count() == 0xbb


def test_temperature_on_sensor_parses_response_correctly():
    expected_temperature = 5.5

    encoded_temperature = struct.pack("<f", expected_temperature)
    assert len(encoded_temperature) == 4

    data_hex = "010222330007020301" + binascii.hexlify(encoded_temperature).decode("ascii").lower()
    print("data_hex = {}".format(data_hex))

    res = TemperatureOnSensorResponse(bytearray_to_response(data_hex, False))

    assert res.trunk_number() == 2
    assert res.sensor_index() == 3
    assert res.is_connected()

    assert res.temperature() == expected_temperature


def test_sensor_unique_address_parsed_works_correctly():
    expected_sensor_address = "aabbccddeeff2233"
    assert len(expected_sensor_address) == 8 * 2

    data_hex = "01022233000a0203" + expected_sensor_address
    r = SensorUniqueIdResponse(bytearray_to_response(data_hex, False))

    assert r.trunk_number() == 0x02
    assert r.sensor_index() == 0x03
    assert r.unique_address() == binascii.unhexlify(expected_sensor_address)


def test_temperatures_on_trunk_parser_successfully_parse_data():
    data_hex = "0102223300"

    expected_temperature = 5.5
    encoded_temperature = struct.pack("<f", expected_temperature)
    assert len(encoded_temperature) == 4

    # adding data for all sensors
    trunks_data = "01" + binascii.hexlify(encoded_temperature).decode("ascii").lower()
    trunks_data = MAX_SENSORS_PER_TRUNK * trunks_data

    # adding trunk number
    trunks_data = "07" + trunks_data

    assert len(trunks_data) % 2 == 0
    data_hex += "{:2x}".format(len(trunks_data) // 2) + trunks_data

    res = TemperatureOnTrunkResponse(bytearray_to_response(data_hex, False))

    assert res.trunk_number() == 7

    for index in range(MAX_SENSORS_PER_TRUNK):
        assert res.is_connected(index)
        assert res.temperature(index) == expected_temperature


def test_session_id_response_parser_successfully_parses_data():
    res = SessionIdResponse(bytearray_to_response("010222330004aabbccdd", False))

    assert res.session_id() == bytearray([0xaa, 0xbb, 0xcc, 0xdd])


def test_controller_response_address_parser_parses_successfully():
    res = ControllerNewAddressResponse(bytearray_to_response("010222330001ee", False))

    assert res.new_address() == 0xee


def test_trunk_unique_addresses_parseer_successfully_parses_valid_data():
    expected_sensor_address = "aabbccddeeff2233"

    data_hex = "0102223300"
    trunks_data = "07" + MAX_SENSORS_PER_TRUNK * (expected_sensor_address + "00")

    data_hex += "{:2x}".format(len(trunks_data) // 2) + trunks_data

    res = SensorUniqueAddressOnTrunkResponse(bytearray_to_response(data_hex, False))

    assert res.trunk_number() == 7
    assert res.sensors_count() == MAX_SENSORS_PER_TRUNK

    for index in range(MAX_SENSORS_PER_TRUNK):
        assert not res.is_error_detected(index)
        assert res.sensor_unique_address(index) == binascii.unhexlify(expected_sensor_address)
