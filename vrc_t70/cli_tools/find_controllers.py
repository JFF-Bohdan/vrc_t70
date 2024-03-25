import functools
import signal
import threading
import time
import typing

import click

import configargparse

import humanize

from loguru import logger

import terminaltables

import tqdm

from vrc_t70 import defaults
from vrc_t70 import exceptions
from vrc_t70 import limitations
from vrc_t70 import shared
from vrc_t70.cli_tools import basic_arg_parser
from vrc_t70.communicator import communicator


def signal_handler(stop_event: threading.Event, signum, frame):
    logger.warning("Search termination requested...")
    stop_event.set()


def extend_parser(parser: configargparse.ArgumentParser) -> configargparse.ArgumentParser:
    parser.add_argument(
        "-m",
        "--min",
        action="store",
        help="Min address for search",
        type=int,
        default=limitations.MIN_CONTROLLER_ADDRESS
    )

    parser.add_argument(
        "-x",
        "--max",
        action="store",
        help="Max address for search",
        type=int,
        default=limitations.MAX_CONTROLLER_ADDRESS
    )

    parser.add_argument(
        "-r",
        "--retries",
        action="store",
        help="Max retries count for request",
        type=int,
        default=defaults.DEFAULT_MAX_RETRIES_FOR_REQUEST
    )

    return parser


def generate_table_report(devices: typing.Iterable[int]):
    data = [
        ("Address (decimal)", "Address (hex)")
    ]

    for address in devices:
        data.append(
            (f"{address}", f"0x{address:02x}")
        )

    table = terminaltables.AsciiTable(table_data=data)
    return table.table


def scan_for_controllers(
        connection: communicator.VrcT70Communicator,
        scan_terminated_by_user: threading.Event,
        min_address: int,
        max_address: int
) -> set:
    connection.raise_exception_on_response_with_wrong_address = True

    result = set()
    with tqdm.trange(
            min_address,
            max_address,
            postfix=[dict(devices_count=len(result))],
            unit="rqs"
    ) as targets_range:
        for device_address in targets_range:
            if scan_terminated_by_user.wait(timeout=0.0):
                logger.warning("Search terminated by user...")
                break

            try:
                connection.address = device_address
                connection.ping()

                logger.info(f"Device found with address {device_address}")
                result.add(device_address)
                targets_range.postfix[0]["devices_count"] = len(result)
                targets_range.update()
            except exceptions.ErrorResponseFromControllerWithWrongAddress as e:
                result.add(e.unexpected_address)
            except exceptions.ErrorNoResponseFromController:
                continue

    return result


@click.command(
    name="find-controllers",
    context_settings=dict(ignore_unknown_options=True, allow_extra_args=True),
    add_help_option=False
)
@click.argument("additional_args", nargs=-1, type=click.UNPROCESSED)
def find_controllers(additional_args):
    scan_terminated_by_user = threading.Event()

    arg_parser = basic_arg_parser.create_basic_parser()
    arg_parser = extend_parser(arg_parser)
    args = arg_parser.parse_args(additional_args)

    limitations.validate_controller_address(args.min, "Invalid min value for controller address, ")
    limitations.validate_controller_address(args.max, "Invalid max value for controller address, ")

    partial_signal_handler = functools.partial(signal_handler, scan_terminated_by_user)
    signal.signal(signal.SIGINT, partial_signal_handler)

    logger.info("Searching for controllers")
    timestamp_begin = time.monotonic()

    timeout = args.timeout if args.timeout else defaults.DEFAULT_TIMEOUT

    found_devices = set()
    port_successfully_opened = False
    uart = None
    try:
        logger.info("Opening port ...")
        uart = shared.init_serial(
            uart_name=args.port,
            uart_speed=args.speed,
            wait_delay=timeout
        )
        port_successfully_opened = True

        connection = communicator.VrcT70Communicator(
            port=uart,
            address=args.min,
            requests_retries_count=args.retries
        )
        found_devices = scan_for_controllers(
            connection=connection,
            scan_terminated_by_user=scan_terminated_by_user,
            min_address=args.min,
            max_address=args.max

        )
    finally:
        time_elapsed_human_readable = humanize.precisedelta(
            shared.timedelta_from_monotonic_time(timestamp_begin),
            minimum_unit="milliseconds", format="%0.2f"
        )
        logger.info(f"Scan finished in {time_elapsed_human_readable}")

        if port_successfully_opened:
            if found_devices:
                table_report = generate_table_report(found_devices)
                logger.info(f"Found devices with addresses:\n{table_report}")
            else:
                logger.warning("No devices found")
        else:
            logger.error("There was problem opening port")

        if uart:
            logger.info("Closing UART")
            uart.close()
