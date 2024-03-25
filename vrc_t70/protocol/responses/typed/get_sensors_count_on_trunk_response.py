from vrc_t70 import exceptions
from vrc_t70 import limitations
from vrc_t70.protocol.responses import base_response
from vrc_t70.protocol.responses import raw_response_data


class GetSensorsCountOnTrunkResponse(base_response.BaseResponse):
    """
    Response for request of sensors count on a trunk
    """
    def __init__(
        self,
        raw_response: raw_response_data.RawResponseData
    ):
        super().__init__(raw_response=raw_response)
        if (not self.raw_response.payload) or (len(self.raw_response.payload) != 2):
            raise exceptions.ErrorWrongPayloadLength()

        self.trunk_number = self.raw_response.payload[0]

        limitations.validate_sensor_index(self.raw_response.payload[1])
        self.sensors_count = self.raw_response.payload[1]
