import typing

from vrc_t70 import limitations
from vrc_t70.protocol import requests


class GetTemperatureOfSensorOnTrunkRequest(requests.BaseRequest):
    """
    Requests temperature on a specific sensors on a trunk
    """
    def __init__(
            self,
            trunk_number: int,
            sensor_index: int,
            address: typing.Optional[int] = None,
            sequence_id: typing.Optional[int] = None,
            additional_wait_time_for_response: typing.Optional[float] = 0.2,
    ):
        limitations.validate_trunk_number(trunk_number)
        limitations.validate_sensor_index(sensor_index)

        super().__init__(
            address=address,
            request_id=requests.RequestCodes.GET_TEMPERATURE_OF_SENSOR_ON_TRUNK,
            sequence_id=sequence_id,
            data=bytes([trunk_number, sensor_index]),
            additional_wait_time_for_response=additional_wait_time_for_response,
        )
