from tests.support import common_packets

from vrc_t70.protocol.requests import set_controller_new_address_request


def test_can_serialize_set_controller_new_address_request():
    request = set_controller_new_address_request.SetControllerNewAddressRequest(
        address=0x08,
        sequence_id=0x2233,
        new_controller_address=42
    )

    assert bytes(request) == common_packets.SET_CONTROLLER_NEW_ADDRESS_REQUEST