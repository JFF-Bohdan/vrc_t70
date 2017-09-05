import binascii

import serial

from vrc_t70.communicator import VrcT70Communicator
from vrc_t70.limitations import MAX_TRUNKS_COUNT


def main():
    serial = init_serial("com15")
    communicator = VrcT70Communicator(serial, controller_address=0x01)

    print("initializing communication...")
    communicator.ping(0xaabb)

    print("scanning for devices...")
    devices_count_per_trunk = rescan_devices_on_all_trunks(communicator)

    print()
    print("--==Bulk data processing commands==--")

    for trunk_number, devices_count in enumerate(devices_count_per_trunk):
        trunk_number += 1

        print("Trunk #{} [{} device(s)]:".format(trunk_number, devices_count))

        temperatures = communicator.get_temperature_on_trunk(trunk_number)
        assert temperatures.temperatures_count() == devices_count

        addresses = communicator.get_devices_unique_addresses_on_trunk(trunk_number)
        assert devices_count == addresses.devices_count()

        for device_index in range(devices_count):
            is_connected = temperatures.is_connected(device_index)
            assert is_connected
            temperature = temperatures.temperature(device_index)

            assert not addresses.is_error_detected(device_index)
            uniq_number = addresses.device_unique_address(device_index)

            print(
                "\t[{}]:\t{:.2f} C\t[ number: {} ]".format(
                    device_index,
                    temperature,
                    binascii.hexlify(uniq_number).decode("ascii")
                )
            )

    print()
    print("--==Simple data processing commands==--")
    for trunk_number, devices_count in enumerate(devices_count_per_trunk):
        trunk_number += 1
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


def rescan_devices_on_all_trunks(communicator):
    res = []

    for trunk_number in range(1, MAX_TRUNKS_COUNT + 1):
        r = communicator.rescan_devices_on_trunk(trunk_number)
        res.append(r.devices_count())

    return res


def init_serial(uart_name, uart_speed=115200):
    return serial.Serial(
        uart_name,
        baudrate=uart_speed,
        bytesize=serial.EIGHTBITS,
        timeout=0.5,
        parity=serial.PARITY_NONE,
        stopbits=serial.STOPBITS_ONE
    )


if __name__ == "__main__":
    res = main()
    exit(res)
