from tests.support import common_packets

from vrc_t70.protocol import responses


def test_can_parse_set_controller_new_address_response():
    raw_response = responses.deserialize(data=common_packets.SET_CONTROLLER_NEW_ADDRESS_RESPONSE)
    response = responses.SetControllerNewAddressResponse(raw_response=raw_response)

    assert response.new_address == 42
