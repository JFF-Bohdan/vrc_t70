import binascii

import serial

from vrc_t70.communicator import VrcT70Communicator
from vrc_t70.limitations import MAX_TRUNKS_COUNT


def main():
    serial = init_serial()
    communicator = VrcT70Communicator(serial, controller_address=0x01)

    communicator.ping(sequence_id=0xaabb)
    for trunk_number in range(1, MAX_TRUNKS_COUNT + 1):
        r = communicator.rescan_devices_on_trunk(trunk_number)
        devices_count = r.devices_count()
        print("Trunk #{} [{} device(s)]:".format(trunk_number, devices_count))

        for device_index in range(devices_count):
            r = communicator.get_temperature_on_device(trunk_number, device_index)
            temperature = r.temperature()

            r = communicator.get_device_unique_number(trunk_number, device_index)
            uniq_number = r.unique_number()

            print(
                "\t[{}]:\t{:.2f} C\t[ number: {} ]".format(
                    device_index,
                    temperature,
                    binascii.hexlify(uniq_number).decode("ascii")
                )
            )

    serial.close()


def init_serial():
    return serial.Serial(
        "COM15",
        baudrate=115200,
        bytesize=serial.EIGHTBITS,
        timeout=1,
        parity=serial.PARITY_NONE,
        stopbits=serial.STOPBITS_ONE
    )


if __name__ == "__main__":
    res = main()
    exit(res)
