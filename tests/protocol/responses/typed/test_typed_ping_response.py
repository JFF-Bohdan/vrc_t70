from tests.support import common_packets

from vrc_t70.protocol import responses


def test_ping_response():
    raw_response = responses.deserialize(data=bytes(common_packets.PING_RESPONSE))
    response = responses.PingResponse(raw_response=raw_response)
    assert response.raw_response.payload is None
