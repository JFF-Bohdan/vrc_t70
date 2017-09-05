from .base_communicator import VrcT70CommunicatorBase
from .commands import VrcT70Commands
from .request import VrcT70Request
from .response import DeviceUniqueId, TemperatureOnDevice, TrunkRescanResult


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

        return TrunkRescanResult(res)

    def get_temperature_on_device(self, trunk_number, device_index, sequence_id=0x0000):
        res = self.send_command(
            VrcT70Request(
                self.controller_address,
                VrcT70Commands.GET_TEMPERATURE_OF_DEVICE,
                sequence_id,
                bytearray([trunk_number & 0xff, device_index & 0xff])
            )
        )

        return TemperatureOnDevice(res)

    def get_device_unique_number(self, trunk_number, device_index, sequence_id=0x0000):
        res = self.send_command(
            VrcT70Request(
                self.controller_address,
                VrcT70Commands.GET_DEVICE_UNIQUE_NUMBER,
                sequence_id,
                bytearray([trunk_number & 0xff, device_index & 0xff])
            )
        )

        return DeviceUniqueId(res)
