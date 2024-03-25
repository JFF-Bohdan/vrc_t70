import math

from tests.support import common_packets

from vrc_t70.protocol.responses import raw_response_data
from vrc_t70.protocol.responses.typed import get_temperatures_on_trunk_response


def test_can_parse_get_temperatures_on_trunk_response_with_multiple_sensors():
    raw_response = raw_response_data.deserialize(data=common_packets.GET_TEMPERATURES_ON_TRUNK_RESPONSE_5_SENSORS)
    response = get_temperatures_on_trunk_response.GetTemperaturesOnTrunkResponse(
        raw_response=raw_response
    )

    expected_info = [
        (True, 19.9792),
        (True, 20.94),
        (True, 18.44),
        (False, None),
        (True, 19.62)
    ]

    sensors_temperature = response.sensors_temperature
    assert len(sensors_temperature) == len(expected_info)

    for index, (expected_is_connected, expected_temperature) in enumerate(expected_info):
        sensor_info = sensors_temperature[index]
        assert sensor_info.trunk_number == 4
        assert sensor_info.sensor_index == index
        assert sensor_info.is_connected == expected_is_connected
        if expected_temperature:
            assert math.isclose(sensor_info.temperature, expected_temperature, abs_tol=0.01)
        else:
            assert sensor_info.temperature is None


def test_can_parse_get_temperatures_on_trunk_response_with_one_sensor():
    raw_response = raw_response_data.deserialize(data=common_packets.GET_TEMPERATURES_ON_TRUNK_RESPONSE_1_SENSOR)
    response = get_temperatures_on_trunk_response.GetTemperaturesOnTrunkResponse(
        raw_response=raw_response
    )
    sensors_temperature = response.sensors_temperature
    assert len(sensors_temperature) == 1

    assert sensors_temperature[0].trunk_number == 4
    assert sensors_temperature[0].sensor_index == 0
    assert sensors_temperature[0].is_connected
    assert math.isclose(sensors_temperature[0].temperature, 20.94, abs_tol=0.01)
