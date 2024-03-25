from tests.support import common_packets

from vrc_t70.protocol.requests import get_sensors_count_on_trunk_request


def test_can_serialize_get_sensors_count_on_trunk():
    commmand = get_sensors_count_on_trunk_request.GetSensorsCountOnTrunkRequest(
        address=0x08,
        sequence_id=0x2233,
        trunk_number=4,
    )

    assert bytes(commmand) == common_packets.GET_SENSORS_COUNT_ON_TRUNK_REQUEST
