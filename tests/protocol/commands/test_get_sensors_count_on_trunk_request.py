from tests.support import common_packets

from vrc_t70.protocol import requests


def test_can_serialize_get_sensors_count_on_trunk():
    command = requests.GetSensorsCountOnTrunkRequest(
        address=0x08,
        sequence_id=0x2233,
        trunk_number=4,
    )

    assert bytes(command) == common_packets.GET_SENSORS_COUNT_ON_TRUNK_REQUEST
