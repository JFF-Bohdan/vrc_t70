import logging
import threading
import time
import typing

import click

import configargparse

import humanize

import terminaltables

import tqdm

from vrc_t70 import controller_communicator, defaults, exceptions, limitations, shared
from vrc_t70.cli_tools import basic_arg_parser
from vrc_t70.cli_tools import shared as cli_shared


logger = logging.getLogger(__name__)


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
        connection: controller_communicator.VrcT70Communicator,
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
    arg_parser = basic_arg_parser.create_basic_parser_for_single_controller()
    arg_parser = extend_parser(arg_parser)
    args = arg_parser.parse_args(additional_args)

    cli_shared.setup_logging()

    limitations.validate_controller_address(args.min, "Invalid min value for controller address, ")
    limitations.validate_controller_address(args.max, "Invalid max value for controller address, ")

    scan_terminated_by_user = threading.Event()
    cli_shared.register_interception_of_ctrl_c("Search termination requested...", scan_terminated_by_user)

    logger.info("Searching for controllers")
    timestamp_begin = time.monotonic()

    timeout = args.timeout if args.timeout else defaults.DEFAULT_TIMEOUT

    found_devices = set()
    port_successfully_opened = False
    uart = None
    try:
        logger.info("Opening port ...")
        uart = shared.init_serial(
            port_name=args.port,
            baudrate=args.baudrate,
            timeout=timeout
        )
        port_successfully_opened = True

        connection = controller_communicator.VrcT70Communicator(
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
