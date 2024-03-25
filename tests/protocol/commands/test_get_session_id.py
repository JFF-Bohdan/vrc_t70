from tests.support import common_packets

from vrc_t70.protocol.requests import get_session_id_request


def test_can_serialize_get_session_id():
    commmand = get_session_id_request.GetSessionIdRequest(
        address=0x08,
        sequence_id=0x2233
    )

    assert bytes(commmand) == common_packets.GET_SESSION_ID_REQUEST
