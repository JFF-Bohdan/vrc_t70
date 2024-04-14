import typing

from vrc_t70 import limitations
from vrc_t70.protocol import requests


class GetSensorsUniqueAddressOnTrunkRequest(requests.BaseRequest):
    """
    Requests addresses of ALL sensors on a specific trunk
    """
    def __init__(
            self,
            trunk_number: int,
            address: typing.Optional[int] = None,
            sequence_id: typing.Optional[int] = None,
            additional_wait_time_for_response: typing.Optional[float] = 0.250,
    ):
        limitations.validate_trunk_number(trunk_number)

        super().__init__(
            address=address,
            request_id=requests.RequestCodes.GET_SENSORS_UNIQUE_ADDRESS_ON_TRUNK,
            sequence_id=sequence_id,
            data=bytes([trunk_number]),
            additional_wait_time_for_response=additional_wait_time_for_response,
        )
