import typing

from vrc_t70.protocol import requests


class GetSessionIdRequest(requests.BaseRequest):
    """
    Requests session id
    """
    def __init__(
            self,
            address: typing.Optional[int] = None,
            sequence_id: typing.Optional[int] = None,
            additional_wait_time_for_response: typing.Optional[float] = 0.05,
    ):
        super().__init__(
            address=address,
            request_id=requests.RequestCodes.GET_SESSION_ID,
            sequence_id=sequence_id,
            additional_wait_time_for_response=additional_wait_time_for_response,
        )
