from tests.support import common_packets

from vrc_t70.protocol.responses import raw_response_data
from vrc_t70.protocol.responses.typed import set_session_id_response


def test_can_deserialize_set_session_id():
    raw_response = raw_response_data.deserialize(data=common_packets.SET_SESSION_ID_RESPONSE)
    response = set_session_id_response.SetSessionIdResponse(raw_response=raw_response)

    assert response.raw_response == raw_response
    assert response.session_id == 0xdeadbeef
