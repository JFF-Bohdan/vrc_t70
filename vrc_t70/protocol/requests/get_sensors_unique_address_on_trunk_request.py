import typing

from vrc_t70 import limitations
from vrc_t70.protocol.requests import base_request, request_codes


class GetSensorsUniqueAddressOnTrunkRequest(base_request.BaseRequest):
    """
    Requests addresses of ALL sensors on a specific trunk
    """
    def __init__(
            self,
            trunk_number: int,
            address: typing.Optional[int] = None,
            sequence_id: typing.Optional[int] = None,
    ):
        limitations.validate_trunk_number(trunk_number)

        super().__init__(
            address=address,
            request_id=request_codes.RequestCodes.GET_SENSORS_UNIQUE_ADDRESS_ON_TRUNK,
            sequence_id=sequence_id,
            data=bytes([trunk_number])
        )
