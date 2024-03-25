from tests.support import common_packets

from vrc_t70.protocol.responses import raw_response_data
from vrc_t70.protocol.responses.typed import get_sensor_unique_address_on_trunk_response


def test_can_parse_get_sensor_unique_address_on_trunk_response():
    raw_response = raw_response_data.deserialize(data=common_packets.GET_SENSOR_UNIQUE_ADDRESS_ON_TRUNK_RESPONSE)
    response = get_sensor_unique_address_on_trunk_response.GetSensorUniqueAddressOnTrunkResponse(
        raw_response=raw_response
    )

    assert response.trunk_number == 4
    assert response.sensor_index == 5
    assert response.sensor_address == 0x28ff2c7d901501c1
