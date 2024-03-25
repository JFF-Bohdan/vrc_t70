from vrc_t70 import exceptions
from vrc_t70 import limitations
from vrc_t70.protocol.responses import base_response
from vrc_t70.protocol.responses import raw_response_data


class GetSensorUniqueAddressOnTrunkResponse(base_response.BaseResponse):
    """
    Response for request of single specific sensor address on a trunk
    """
    def __init__(
        self,
        raw_response: raw_response_data.RawResponseData
    ):
        super().__init__(raw_response=raw_response)
        if (not self.raw_response.payload) or (len(self.raw_response.payload) != 10):
            raise exceptions.ErrorWrongPayloadLength()

        self.trunk_number = self.raw_response.payload[0]
        limitations.validate_trunk_number(self.trunk_number)

        self.sensor_index = self.raw_response.payload[1]
        limitations.validate_sensor_index(self.sensor_index)

        sensor_address = 0x00
        data = self.raw_response.payload[2:]
        for byte in data:
            sensor_address <<= 8
            sensor_address |= byte

        self.sensor_address = sensor_address
