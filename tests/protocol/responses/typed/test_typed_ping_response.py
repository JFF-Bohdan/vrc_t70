from tests.support import common_packets

from vrc_t70.protocol.responses import raw_response_data
from vrc_t70.protocol.responses.typed import ping_response


def test_ping_response():
    raw_response = raw_response_data.deserialize(data=bytes(common_packets.PING_RESPONSE))
    response = ping_response.PingResponse(raw_response=raw_response)
    assert response.raw_response.payload is None
