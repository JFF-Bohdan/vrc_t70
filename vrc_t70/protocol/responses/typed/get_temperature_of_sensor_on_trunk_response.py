from vrc_t70 import exceptions
from vrc_t70 import limitations
from vrc_t70 import shared
from vrc_t70.protocol.responses import base_response
from vrc_t70.protocol.responses import raw_response_data
from vrc_t70.protocol.responses.typed import data_types


class GetTemperatureOfSensorOnTrunkResponse(base_response.BaseResponse):
    """
    Response for request of temperature of specific sensor on a trunk
    """
    def __init__(
        self,
        raw_response: raw_response_data.RawResponseData
    ):
        super().__init__(raw_response=raw_response)
        if (not self.raw_response.payload) or (len(self.raw_response.payload) != 7):
            raise exceptions.ErrorWrongPayloadLength()

        trunk_number = self.raw_response.payload[0]
        sensor_index = self.raw_response.payload[1]

        is_connected = self.raw_response.payload[2]
        limitations.validate_bool(is_connected)
        is_connected = bool(is_connected)

        if is_connected:
            temperature, = shared.decode_float(self.raw_response.payload[3:])
        else:
            temperature = None

        self.sensor_temperature = data_types.SensorTemperatureInfo(
            trunk_number=trunk_number,
            sensor_index=sensor_index,
            is_connected=is_connected,
            temperature=temperature
        )
