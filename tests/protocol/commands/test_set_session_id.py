from tests.support import common_packets

from vrc_t70.protocol import requests


def test_can_serialize_set_session_id():
    request = requests.SetSessionIdRequest(
        address=0x08,
        sequence_id=0x2233,
        session_id=0xdeadbeef,
    )

    assert bytes(request) == common_packets.SET_SESSION_ID_REQUEST
