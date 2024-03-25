from tests.support import common_packets

from vrc_t70.protocol.requests import set_session_id_request


def test_can_serialize_set_session_id():
    request = set_session_id_request.SetSessionIdRequest(
        address=0x08,
        sequence_id=0x2233,
        session_id=0xdeadbeef,
    )

    assert bytes(request) == common_packets.SET_SESSION_ID_REQUEST
