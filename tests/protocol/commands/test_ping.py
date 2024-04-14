from tests.support import common_packets

from vrc_t70.protocol import requests


def test_can_serialize_ping():
    request = requests.PingRequest(
        address=0x08,
        sequence_id=0x2233,
    )

    assert bytes(request) == common_packets.PING_REQUEST
