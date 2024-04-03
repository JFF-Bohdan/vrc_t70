import typing

from vrc_t70.protocol.requests import base_request, request_codes


class PingRequest(base_request.BaseRequest):
    """
    Performs ping request. Can be used to check if controller is available for communication.
    """
    def __init__(
            self,
            sequence_id: typing.Optional[int] = None,
            address: typing.Optional[int] = None,
            additional_wait_time_for_response: typing.Optional[float] = 0.0,
    ):
        super().__init__(
            address=address,
            request_id=request_codes.RequestCodes.PING,
            sequence_id=sequence_id,
            additional_wait_time_for_response=additional_wait_time_for_response,
        )