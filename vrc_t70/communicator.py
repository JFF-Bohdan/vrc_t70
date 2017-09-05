from .base_communicator import VrcT70CommunicatorBase
from .commands import VrcT70Commands
from .request import VrcT70Request
from .response import (DeviceUniqueIdResponse, DevicesUniqueAddressesOnTrunkResponse, NewAddressResponse,
                       SessionIdResponse, TemperatureOnDeviceResponse, TemperatureOnTrunkResponse,
                       TrunkSensortsCountResponse)


class VrcT70Communicator(VrcT70CommunicatorBase):
    def __init__(self, serial, controller_address=0x01):
        super().__init__(serial, controller_address)

    def ping(self, sequence_id=0x0000):
        return self.send_command(
            VrcT70Request(
                self.controller_address,
                VrcT70Commands.PING,
                sequence_id
            )
        )

    def rescan_devices_on_trunk(self, trunk_number, sequence_id=0x0000):
        res = self.send_command(
            VrcT70Request(
                self.controller_address,
                VrcT70Commands.RESCAN_DEVICES_ON_TRUNK,
                sequence_id,
                bytearray([trunk_number & 0xff])
            )
        )

        return TrunkSensortsCountResponse(res)

    def get_temperature_on_device(self, trunk_number, device_index, sequence_id=0x0000):
        res = self.send_command(
            VrcT70Request(
                self.controller_address,
                VrcT70Commands.GET_TEMPERATURE_OF_DEVICE,
                sequence_id,
                bytearray([trunk_number & 0xff, device_index & 0xff])
            )
        )

        return TemperatureOnDeviceResponse(res)

    def get_device_unique_number(self, trunk_number, device_index, sequence_id=0x0000):
        res = self.send_command(
            VrcT70Request(
                self.controller_address,
                VrcT70Commands.GET_DEVICE_UNIQUE_NUMBER,
                sequence_id,
                bytearray([trunk_number & 0xff, device_index & 0xff])
            )
        )

        return DeviceUniqueIdResponse(res)

    def get_temperature_on_trunk(self, trunk_number, sequence_id=0x0000):
        res = self.send_command(
            VrcT70Request(
                self.controller_address,
                VrcT70Commands.GET_TEMPERATURES_ON_TRUNK,
                sequence_id,
                bytearray([trunk_number & 0xff])
            )
        )

        return TemperatureOnTrunkResponse(res)

    def get_devices_unique_addresses_on_trunk(self, trunk_number, sequence_id=0x0000):
        res = self.send_command(
            VrcT70Request(
                self.controller_address,
                VrcT70Commands.GET_DEVICES_UNIQUE_ON_TRUNK,
                sequence_id,
                bytearray([trunk_number & 0xff])
            )
        )

        return DevicesUniqueAddressesOnTrunkResponse(res)

    def get_session_id(self, sequence_id=0x0000):
        res = self.send_command(
            VrcT70Request(
                self.controller_address,
                VrcT70Commands.GET_SESSION_ID,
                sequence_id
            )
        )

        return SessionIdResponse(res)

    def set_session_id(self, session_id, sequence_id=0x0000):
        res = self.send_command(
            VrcT70Request(
                self.controller_address,
                VrcT70Commands.SET_SESSION_ID,
                sequence_id,
                session_id[0: 4]
            )
        )

        return SessionIdResponse(res)

    def get_sensors_count_on_trunk(self, trunk_number, sequence_id=0x0000):
        res = self.send_command(
            VrcT70Request(
                self.controller_address,
                VrcT70Commands.GET_SENSORS_COUNT_ON_TRUNK,
                sequence_id,
                bytearray([trunk_number])
            )
        )

        return TrunkSensortsCountResponse(res)

    def set_new_address(self, new_address, sequence_id=0x0000):
        res = self.send_command(
            VrcT70Request(
                self.controller_address,
                VrcT70Commands.SET_NEW_DEVICE_ADDRESS,
                sequence_id,
                bytearray([new_address])
            )
        )

        return NewAddressResponse(res)
