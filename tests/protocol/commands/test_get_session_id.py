from tests.support import common_packets

from vrc_t70.protocol import requests


def test_can_serialize_get_session_id():
    commmand = requests.GetSessionIdRequest(
        address=0x08,
        sequence_id=0x2233,
    )

    assert bytes(commmand) == common_packets.GET_SESSION_ID_REQUEST
