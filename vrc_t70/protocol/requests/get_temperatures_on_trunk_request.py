import typing

from vrc_t70 import limitations
from vrc_t70.protocol.requests import base_request, request_codes


class GetTemperaturesOnTrunkRequest(base_request.BaseRequest):
    """
    Requests temperatures of ALL sensors on a trunk
    """
    def __init__(
            self,
            trunk_number: int,
            address: typing.Optional[int] = None,
            sequence_id: typing.Optional[int] = None,
            additional_wait_time_for_response: typing.Optional[float] = 0.0,
    ):
        limitations.validate_trunk_number(trunk_number)

        super().__init__(
            address=address,
            request_id=request_codes.RequestCodes.GET_TEMPERATURES_ON_TRUNK,
            sequence_id=sequence_id,
            data=bytes([trunk_number]),
            additional_wait_time_for_response=additional_wait_time_for_response,
        )
