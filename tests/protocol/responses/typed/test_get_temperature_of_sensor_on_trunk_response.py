import math

from tests.support import common_packets

from vrc_t70.protocol import responses


def test_can_parse_get_temperature_of_sensor_on_trunk_response():
    raw_response = responses.deserialize(data=common_packets.GET_TEMPERATURE_OF_SENSOR_ON_TRUNK_RESPONSE)
    response = responses.GetTemperatureOfSensorOnTrunkResponse(
        raw_response=raw_response
    )

    assert response.sensor_temperature.trunk_number == 4
    assert response.sensor_temperature.sensor_index == 5
    assert response.sensor_temperature.is_connected
    assert math.isclose(response.sensor_temperature.temperature, 19.979, abs_tol=0.001)


def test_not_deserializes_temperature_on_error():
    raw_response = responses.deserialize(data=common_packets.GET_TEMPERATURE_OF_SENSOR_ON_TRUNK_RESPONSE_V2)
    response = responses.GetTemperatureOfSensorOnTrunkResponse(
        raw_response=raw_response
    )

    assert response.sensor_temperature.trunk_number == 4
    assert response.sensor_temperature.sensor_index == 5
    assert not response.sensor_temperature.is_connected
    assert response.sensor_temperature.temperature is None
