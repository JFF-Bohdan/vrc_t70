from tests.support import common_packets

from vrc_t70.protocol.responses import raw_response_data
from vrc_t70.protocol.responses.typed import set_controller_new_address_response


def test_can_parse_set_controller_new_address_response():
    raw_response = raw_response_data.deserialize(data=common_packets.SET_CONTROLLER_NEW_ADDRESS_RESPONSE)
    response = set_controller_new_address_response.SetControllerNewAddressResponse(raw_response=raw_response)

    assert response.new_address == 42
