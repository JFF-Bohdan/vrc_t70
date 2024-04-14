from tests.support import common_packets

from vrc_t70.protocol import responses


def test_can_parse_rescan_sensors_on_trunk_response():
    raw_response = responses.deserialize(data=common_packets.RESCAN_SENSORS_ON_TRUNK_RESPONSE)
    response = responses.RescanSensorsOnTrunkResponse(raw_response=raw_response)

    assert response.trunk_number == 4
    assert response.sensors_count == 3
