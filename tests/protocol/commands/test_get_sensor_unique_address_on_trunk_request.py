from tests.support import common_packets

from vrc_t70.protocol.requests import get_sensor_unique_address_on_trunk_request


def test_can_serialize_get_sensor_unique_address_on_trunk_request():
    commmand = get_sensor_unique_address_on_trunk_request.GetSensorUniqueAddressOnTrunkRequest(
        address=0x08,
        sequence_id=0x2233,
        trunk_number=4,
        sensor_index=5
    )

    assert bytes(commmand) == common_packets.GET_SENSOR_UNIQUE_ADDRESS_ON_TRUNK_REQUEST
