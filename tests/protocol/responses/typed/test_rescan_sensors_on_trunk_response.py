from tests.support import common_packets

from vrc_t70.protocol.responses import raw_response_data
from vrc_t70.protocol.responses.typed import rescan_sensors_on_trunk_response


def test_can_parse_rescan_sensors_on_trunk_response():
    raw_response = raw_response_data.deserialize(data=common_packets.RESCAN_SENSORS_ON_TRUNK_RESPONSE)
    response = rescan_sensors_on_trunk_response.RescanSensorsOnTrunkResponse(raw_response=raw_response)

    assert response.trunk_number == 4
    assert response.sensors_count == 3
