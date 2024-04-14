import typing

from vrc_t70.protocol import requests


class SetSessionIdRequest(requests.BaseRequest):
    """
    Sets new session id.
    """
    def __init__(
            self,
            session_id: int,
            address: typing.Optional[int] = None,
            sequence_id: typing.Optional[int] = None,
            additional_wait_time_for_response: typing.Optional[float] = 0.250,
    ):
        session_id = session_id & 0xffffffff
        super().__init__(
            address=address,
            request_id=requests.RequestCodes.SET_SESSION_ID,
            sequence_id=sequence_id,
            data=bytes(
                [
                    (session_id & 0xff000000) >> 24,
                    (session_id & 0xff0000) >> 16,
                    (session_id & 0xff00) >> 8,
                    session_id & 0xff
                ]
            ),
            additional_wait_time_for_response=additional_wait_time_for_response,
        )
