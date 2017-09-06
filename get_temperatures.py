import binascii
import random

import serial

from tools_shared.cmd_line_parser import get_args

from vrc_t70.communicator import VrcT70Communicator
from vrc_t70.limitations import MAX_TRUNKS_COUNT


def main():
    args = get_args()

    uart = init_serial(args.uart_name, args.uart_speed)
    communicator = VrcT70Communicator(uart, controller_address=args.device_address)

    print("initializing communication with device {0} [0x{0:02x}]...".format(args.device_address))
    print("\tping")
    communicator.ping()

    new_session_id = random_byte_array(4)
    print("\tinitializing session id with {}".format(my_hexlify(new_session_id)))
    r = communicator.set_session_id(new_session_id)

    assert r.session_id() == new_session_id

    r = communicator.get_session_id()
    print("\tsession_id = {}".format(my_hexlify(r.session_id())))
    assert r.session_id() == new_session_id

    print("scanning for sensors...")
    sensors_count_per_trunk = rescan_devices_on_all_trunks(communicator)

    print()
    print("--==Bulk data processing commands==--")

    for trunk_number, devices_count in enumerate(sensors_count_per_trunk):
        trunk_number += 1

        print("Trunk #{} [{} device(s)]:".format(trunk_number, devices_count))

        temperatures = communicator.get_temperature_on_trunk(trunk_number)
        assert temperatures.temperatures_count() == devices_count

        addresses = communicator.get_sensors_unique_addresses_on_trunk(trunk_number)
        assert devices_count == addresses.sensors_count()

        for sensor_index in range(devices_count):
            is_connected = temperatures.is_connected(sensor_index)
            assert is_connected
            temperature = temperatures.temperature(sensor_index)

            assert not addresses.is_error_detected(sensor_index)
            uniq_number = addresses.sensor_unique_address(sensor_index)

            print(
                "\t[{}]:\t{:.2f} C\t[ number: {} ]".format(
                    sensor_index,
                    temperature,
                    my_hexlify(uniq_number)
                )
            )

    print()
    print("--==Simple data processing commands==--")
    for trunk_number, devices_count in enumerate(sensors_count_per_trunk):
        trunk_number += 1
        print("Trunk #{} [{} device(s)]:".format(trunk_number, devices_count))

        for sensor_index in range(devices_count):
            r = communicator.get_temperature_on_sensor_on_trunk(trunk_number, sensor_index)
            temperature = r.temperature()

            r = communicator.get_sensor_unique_address_on_trunk(trunk_number, sensor_index)
            uniq_number = r.unique_number()

            print(
                "\t[{}]:\t{:.2f} C\t[ number: {} ]".format(
                    sensor_index,
                    temperature,
                    my_hexlify(uniq_number)
                )
            )

    uart.close()


def rescan_devices_on_all_trunks(communicator):
    res = []

    for trunk_number in range(1, MAX_TRUNKS_COUNT + 1):
        r = communicator.rescan_sensors_on_trunk(trunk_number)
        res.append(r.sensors_count())

    return res


def init_serial(uart_name, uart_speed):
    return serial.Serial(
        uart_name,
        baudrate=uart_speed,
        bytesize=serial.EIGHTBITS,
        timeout=0.5,
        parity=serial.PARITY_NONE,
        stopbits=serial.STOPBITS_ONE
    )


def my_hexlify(data):
    return binascii.hexlify(data).decode("ascii")


def random_byte_array(length):
    return bytearray((random.getrandbits(8) for _ in range(length)))


if __name__ == "__main__":
    res = main()
    exit(res)
