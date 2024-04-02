import typing

from vrc_t70 import limitations
from vrc_t70.protocol.requests import base_request, request_codes


class SetControllerNewAddressRequest(base_request.BaseRequest):
    """
    Configures new address of controller
    """
    def __init__(
            self,
            new_controller_address: int,
            address: typing.Optional[int] = None,
            sequence_id: typing.Optional[int] = None,
            additional_wait_time_for_response: typing.Optional[float] = 0.2,
    ):
        limitations.validate_controller_address(new_controller_address)

        super().__init__(
            address=address,
            request_id=request_codes.RequestCodes.SET_CONTROLLER_NEW_ADDRESS,
            sequence_id=sequence_id,
            data=bytes([new_controller_address]),
            additional_wait_time_for_response=additional_wait_time_for_response,
        )
