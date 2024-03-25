from vrc_t70 import exceptions
from vrc_t70 import limitations
from vrc_t70.protocol.responses import base_response
from vrc_t70.protocol.responses import raw_response_data
from vrc_t70.protocol.responses.typed import data_types


class GetSensorsUniqueAddressOnTrunkResponse(base_response.BaseResponse):
    """
    Response for request of ALL sensors addresses on a trunk
    """
    def __init__(
        self,
        raw_response: raw_response_data.RawResponseData
    ):
        super().__init__(raw_response=raw_response)
        self.sensors_address: list[data_types.SensorAddressInfo] = []

        if not self.raw_response.payload:
            raise exceptions.ErrorWrongPayloadLength()

        payload_length = len(self.raw_response.payload)
        if (
                (payload_length < 1) or
                ((payload_length - 1) % 9 != 0)
        ):
            raise exceptions.ErrorWrongPayloadLength()

        sensors_count = (payload_length - 1) // 9
        # Checking if have too many sensors
        if sensors_count > limitations.MAX_SENSOR_INDEX + 1:
            raise exceptions.ErrorWrongPayloadLength()

        trunk_number = self.raw_response.payload[0]
        limitations.validate_trunk_number(trunk_number)

        offset = 1
        sensor_index = 0
        while offset < payload_length - 1:
            raw_address = self.raw_response.payload[offset: offset + 8]
            sensor_address = 0x00
            for byte in raw_address:
                sensor_address <<= 8
                sensor_address |= byte

            is_error_detected = self.raw_response.payload[offset + 8]
            limitations.validate_bool(is_error_detected)
            is_error_detected = bool(is_error_detected)

            self.sensors_address.append(
                data_types.SensorAddressInfo(
                    trunk_number=trunk_number,
                    sensor_index=sensor_index,
                    address=sensor_address,
                    is_error_detected=is_error_detected
                )
            )

            sensor_index += 1
            offset += 9
