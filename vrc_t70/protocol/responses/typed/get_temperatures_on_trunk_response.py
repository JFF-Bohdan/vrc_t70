from vrc_t70 import exceptions
from vrc_t70 import limitations
from vrc_t70 import shared
from vrc_t70.protocol.responses import base_response
from vrc_t70.protocol.responses import raw_response_data
from vrc_t70.protocol.responses.typed import data_types


class GetTemperaturesOnTrunkResponse(base_response.BaseResponse):
    """
    Response for request of temperatures of ALL sensors on a trunk
    """
    def __init__(
        self,
        raw_response: raw_response_data.RawResponseData
    ):
        super().__init__(raw_response=raw_response)
        self.sensors_temperature: list[data_types.SensorTemperatureInfo] = []

        if not self.raw_response.payload:
            raise exceptions.ErrorWrongPayloadLength()

        payload_length = len(self.raw_response.payload)
        if (
                (payload_length < 1) or
                ((payload_length - 1) % 5 != 0)
        ):
            raise exceptions.ErrorWrongPayloadLength()

        sensors_count = (payload_length - 1) // 5
        if sensors_count > limitations.MAX_SENSOR_INDEX + 1:
            raise exceptions.ErrorWrongPayloadLength()

        trunk_number = self.raw_response.payload[0]
        limitations.validate_trunk_number(trunk_number)

        offset = 1
        sensor_index = 0
        while offset < payload_length - 1:
            is_connected = self.raw_response.payload[offset]
            limitations.validate_bool(is_connected)
            is_connected = bool(is_connected)

            if is_connected:
                temperature, = shared.decode_float(self.raw_response.payload[offset + 1: offset + 1 + 4])
            else:
                temperature = None

            self.sensors_temperature.append(
                data_types.SensorTemperatureInfo(
                    trunk_number=trunk_number,
                    sensor_index=sensor_index,
                    is_connected=is_connected,
                    temperature=temperature
                )
            )

            sensor_index += 1
            offset += 5
