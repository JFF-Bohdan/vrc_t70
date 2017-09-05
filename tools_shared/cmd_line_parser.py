import argparse


def get_args():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "-u",
        "--uart",
        action="store",
        dest="uart_name",
        type=str,
        help="uart name"
    )

    parser.add_argument(
        "-s",
        "--speed",
        action="store",
        dest="uart_speed",
        help="uart speed",
        type=int,
        default=115200
    )

    parser.add_argument(
        "-a",
        "--address",
        action="store",
        dest="device_address",
        help="device address",
        type=int,
        default=0x01
    )

    return parser.parse_args()


def get_scaner_args():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "-u",
        "--uart",
        action="store",
        dest="uart_name",
        type=str,
        help="uart name"
    )

    parser.add_argument(
        "-s",
        "--speed",
        action="store",
        dest="uart_speed",
        help="uart speed",
        type=int,
        default=115200
    )

    parser.add_argument(
        "-d",
        "--delay",
        action="store",
        dest="wait_delay",
        help="wait delay",
        type=float,
        default=0.5
    )

    return parser.parse_args()
