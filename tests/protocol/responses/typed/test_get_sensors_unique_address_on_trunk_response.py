from tests.support import common_packets

from vrc_t70.protocol.responses import raw_response_data
from vrc_t70.protocol.responses.typed import get_sensors_unique_address_on_trunk_response


def test_can_parse_get_sensors_unique_addresses_on_trunk_response_1_sensor():
    raw_response = raw_response_data.deserialize(
        data=common_packets.GET_SENSORS_UNIQUE_ADDRESS_ON_TRUNK_RESPONSE_1_SENSOR
    )
    response = get_sensors_unique_address_on_trunk_response.GetSensorsUniqueAddressOnTrunkResponse(
        raw_response=raw_response
    )
    sensors_address = response.sensors_address
    assert len(sensors_address) == 1

    assert not sensors_address[0].is_error_detected
    assert sensors_address[0].address == 0x28ff2c7d901501c1


def test_can_parse_get_sensors_unique_addresses_on_trunk_response_4_sensors():
    expected_results = (
        (0x28ff2c7d901501c1, False),
        (0x28fffd7f90150155, False),
        (0x28ff6f31901504ab, False),
        (0x28ff0930901504a9, True),
    )
    raw_response = raw_response_data.deserialize(
        data=common_packets.GET_SENSORS_UNIQUE_ADDRESS_ON_TRUNK_RESPONSE_4_SENSORS
    )
    response = get_sensors_unique_address_on_trunk_response.GetSensorsUniqueAddressOnTrunkResponse(
        raw_response=raw_response
    )
    sensors_address_info = response.sensors_address
    assert len(sensors_address_info) == len(expected_results)

    for index, (expected_address, expected_is_error_detected) in enumerate(expected_results):
        sensor_address_info = sensors_address_info[index]

        assert sensor_address_info.trunk_number == 0x04
        assert sensor_address_info.sensor_index == index
        assert sensor_address_info.address == expected_address
        assert sensor_address_info.is_error_detected == expected_is_error_detected


def test_can_parse_get_sensors_unique_addresses_on_trunk_response_10_sensors():
    expected_results = (
        (0x54000001f15c5728, False),
        (0xf8031674dc8aff28, True),
        (0x66041674b616ff28, False),
        (0xf5031674e23eff28, True),
        (0x9f0416805499ff28, False),
        (0x87031674b483ff28, False),
        (0x2818b4490c00007c, True),
        (0x28cc19490c0000bb, True),
        (0x2819ef480c000021, True),
        (0x28c6de49f6b63c55, False)
    )

    raw_response = raw_response_data.deserialize(
        data=common_packets.GET_SENSORS_UNIQUE_ADDRESS_ON_TRUNK_RESPONSE_10_SENSORS
    )
    response = get_sensors_unique_address_on_trunk_response.GetSensorsUniqueAddressOnTrunkResponse(
        raw_response=raw_response
    )
    sensors_address_info = response.sensors_address
    assert len(sensors_address_info) == len(expected_results)

    for index, (expected_address, expected_is_error_detected) in enumerate(expected_results):
        sensor_address_info = sensors_address_info[index]

        assert sensor_address_info.trunk_number == 0x04
        assert sensor_address_info.sensor_index == index
        assert sensor_address_info.address == expected_address
        assert sensor_address_info.is_error_detected == expected_is_error_detected
