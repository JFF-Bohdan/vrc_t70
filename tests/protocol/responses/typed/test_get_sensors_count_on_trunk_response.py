from tests.support import common_packets

from vrc_t70.protocol.responses import raw_response_data
from vrc_t70.protocol.responses.typed import get_sensors_count_on_trunk_response


def test_can_parse_get_sensors_count_on_trunk_response():
    raw_response = raw_response_data.deserialize(data=common_packets.GET_SENSORS_COUNT_ON_TRUNK_RESPONSE)
    response = get_sensors_count_on_trunk_response.GetSensorsCountOnTrunkResponse(raw_response=raw_response)

    assert response.trunk_number == 4
    assert response.sensors_count == 3
