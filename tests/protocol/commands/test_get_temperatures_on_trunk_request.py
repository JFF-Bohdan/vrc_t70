from tests.support import common_packets

from vrc_t70.protocol import requests


def test_can_serialize_get_temperature_of_sensor_on_trunk_request():
    commmand = requests.GetTemperaturesOnTrunkRequest(
        address=0x08,
        sequence_id=0x2233,
        trunk_number=4,
    )

    assert bytes(commmand) == common_packets.GET_TEMPERATURES_ON_TRUNK_REQUEST
