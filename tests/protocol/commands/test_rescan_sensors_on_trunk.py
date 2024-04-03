from tests.support import common_packets

from vrc_t70.protocol.requests import rescan_sensors_on_trunk_request


def test_can_serialize_rescan_sensors_on_trunk():
    request = rescan_sensors_on_trunk_request.RescanSensorsOnTrunkRequest(
        address=0x08,
        sequence_id=0x2233,
        trunk_number=4,
    )

    assert bytes(request) == common_packets.RESCAN_SENSORS_ON_TRUNK_REQUEST