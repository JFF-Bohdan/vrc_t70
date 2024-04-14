from tests.support import common_packets

from vrc_t70.protocol import responses


def test_can_deserialize_get_session_id():
    raw_response = responses.deserialize(data=common_packets.GET_SESSION_ID_RESPONSE)
    response = responses.GetSessionIdResponse(raw_response=raw_response)

    assert response.raw_response == raw_response
    assert response.session_id == 0xdeadbeef
