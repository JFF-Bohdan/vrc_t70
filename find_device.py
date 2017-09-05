import serial

from tools_shared.cmd_line_parser import get_scaner_args

from vrc_t70.communicator import VrcT70Communicator


def main():
    args = get_scaner_args()

    uart = init_serial(args.uart_name, args.uart_speed, args.wait_delay)

    total_devices_count = 0
    print("Searching...")
    communicator = VrcT70Communicator(uart)

    for device_address in range(args.min_address, args.max_address + 1):
        communicator.controller_address = device_address
        try:
            communicator.ping()
            print("\tfound device with address 0x{:02x}".format(device_address))
            total_devices_count += 1
        except Exception as _:
            pass

    print("Done. Total_devices_count = {}".format(total_devices_count))

    uart.close()


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
