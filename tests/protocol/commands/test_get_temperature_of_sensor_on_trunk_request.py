from tests.support import common_packets

from vrc_t70.protocol.requests import get_temperature_of_sensor_on_trunk_request


def test_can_serialize_get_temperature_of_sensor_on_trunk_request():
    commmand = get_temperature_of_sensor_on_trunk_request.GetTemperatureOfSensorOnTrunkRequest(
        address=0x08,
        sequence_id=0x2233,
        trunk_number=4,
        sensor_index=5
    )

    assert bytes(commmand) == common_packets.GET_TEMPERATURE_OF_SENSOR_ON_TRUNK_REQUEST
