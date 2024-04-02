import typing

from vrc_t70.protocol.requests import base_request, request_codes


class GetSessionIdRequest(base_request.BaseRequest):
    """
    Requests session id
    """
    def __init__(
            self,
            address: typing.Optional[int] = None,
            sequence_id: typing.Optional[int] = None,
            additional_wait_time_for_response: typing.Optional[float] = 0.0,
    ):
        super().__init__(
            address=address,
            request_id=request_codes.RequestCodes.GET_SESSION_ID,
            sequence_id=sequence_id,
            additional_wait_time_for_response=additional_wait_time_for_response,
        )
