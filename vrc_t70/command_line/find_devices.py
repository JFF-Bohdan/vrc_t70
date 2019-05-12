import time
from collections import namedtuple

import serial

from terminaltables import AsciiTable

from tools_shared.cmd_line_parser import get_scaner_args

from tqdm import tqdm, trange

from vrc_t70.communicator import VrcT70Communicator


FoundDeviceData = namedtuple("FoundDeviceData", ["seconds_elapsed", "device_address"])


def main():
    args = get_scaner_args()

    uart = init_serial(args.uart_name, args.uart_speed, args.wait_delay)

    total_devices_count = 0
    print("Searching...")
    communicator = VrcT70Communicator(uart)

    found_devices = list()
    tm_begin = time.time()

    with trange(args.min_address, args.max_address + 1, postfix=[dict(devices=0)], unit="rqs") as targets_range:
        for device_address in targets_range:
            communicator.controller_address = device_address
            try:
                communicator.ping()
                tqdm.write("\tfound device with address 0x{:02x}".format(device_address))
                found_device_data = FoundDeviceData(
                    seconds_elapsed=time.time() - tm_begin,
                    device_address=device_address
                )
                found_devices.append(found_device_data)
                targets_range.postfix[0]["devices"] = len(found_devices)
                targets_range.update()

            except Exception as _:
                pass

    found_devices = sorted(found_devices, key=(lambda x: x.device_address))
    result_table_data = [["Timestamp found", "Device Address"]]
    for item in found_devices:
        result_table_data.append(
            [
                round(item.seconds_elapsed, 2),
                "0x{:02x}".format(item.device_address)
            ]
        )

    table = AsciiTable(result_table_data)
    print("")
    print(table.table)
    print("Done. Total_devices_count = {}".format(total_devices_count))

    uart.close()
    return 0


def init_serial(uart_name, uart_speed, wait_delay):
    return serial.Serial(
        uart_name,
        baudrate=uart_speed,
        bytesize=serial.EIGHTBITS,
        timeout=wait_delay,
        parity=serial.PARITY_NONE,
        stopbits=serial.STOPBITS_ONE
    )


if __name__ == "__main__":
    res = main()
    exit(res)
