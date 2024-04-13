import dataclasses
import datetime
import logging.config
import time

import click

import humanize

import terminaltables

from vrc_t70 import controller_communicator, shared
from vrc_t70.cli_tools import basic_arg_parser, shared as cli_shared

DESIRED_SESSION_ID_1 = 0xdeadbeef
DESIRED_SESSION_ID_2 = 0xcafebabe

logger = logging.getLogger(__name__)


@dataclasses.dataclass
class TrunkInfo:
    sensors_count: int = 0
    sensors_addresses: dict[int, int] = dataclasses.field(default_factory=lambda: {})
    sensors_temperatures: dict[int, float] = dataclasses.field(default_factory=lambda: {})


@dataclasses.dataclass
class VrcT70DeviceInfo:
    address: int = 0
    session_id: int = 0
    trunks: dict[int, TrunkInfo] = dataclasses.field(default_factory=lambda: {})


@dataclasses.dataclass
class ScanResults:
    info: VrcT70DeviceInfo
    time_elapsed: datetime.timedelta


def sequential_scan(
        connection: controller_communicator.VrcT70Communicator,
        address: int
) -> ScanResults:
    timestamp_begin = time.monotonic()

    scan_info = VrcT70DeviceInfo(address=address)

    logger.debug(f"Setting session id to 0x{DESIRED_SESSION_ID_1:x}")
    connection.set_session_id(DESIRED_SESSION_ID_1)
    session_id = connection.get_session_id()
    logger.debug(f"Session id: {session_id}")
    scan_info.session_id = session_id

    for trunk_number in shared.trunks_indexes():
        trunk_info = TrunkInfo()
        sensors_count_from_rescan = connection.rescan_sensors_on_trunk(trunk_number=trunk_number)
        if not sensors_count_from_rescan:
            scan_info.trunks[trunk_number] = trunk_info
            continue

        logger.info(f"Sensors count on trunk {trunk_number} is {sensors_count_from_rescan}")

        sensors_count = connection.get_get_sensors_count_on_trunk(trunk_number=trunk_number)
        logger.info(f"Sensors count on trunk {trunk_number} is {sensors_count}")
        assert sensors_count == sensors_count_from_rescan

        trunk_info.sensors_count = sensors_count

        for sensor_index in range(sensors_count):
            sensor_address = connection.get_sensor_unique_address_on_trunk(
                trunk_number=trunk_number,
                sensor_index=sensor_index
            )
            trunk_info.sensors_addresses[sensor_index] = sensor_address

            temperature = connection.get_temperature_of_sensor_on_trunk(
                trunk_number=trunk_number,
                sensor_index=sensor_index
            )
            trunk_info.sensors_temperatures[sensor_index] = temperature

            logger.info(
                f"Temperature of sensor {sensor_index} "
                f"(address: 0x{sensor_address:x}) on trunk {trunk_number} is {round(temperature, 2)}C"
            )

        scan_info.trunks[trunk_number] = trunk_info

    return ScanResults(
        info=scan_info,
        time_elapsed=shared.timedelta_from_monotonic_time(timestamp_begin)
    )


def batched_scan(
        connection: controller_communicator.VrcT70Communicator,
        address: int
) -> ScanResults:
    timestamp_begin = time.monotonic()

    scan_info = VrcT70DeviceInfo(address=address)

    logger.debug(f"Setting session id to 0x{DESIRED_SESSION_ID_2:x}")
    connection.set_session_id(DESIRED_SESSION_ID_2)
    session_id = connection.get_session_id()
    logger.debug(f"Session id: {session_id}")
    scan_info.session_id = session_id

    for trunk_number in shared.trunks_indexes():
        trunk_info = TrunkInfo()
        sensors_count_from_rescan = connection.rescan_sensors_on_trunk(trunk_number=trunk_number)
        logger.info(f"Sensors count on trunk {trunk_number} is {sensors_count_from_rescan}")
        trunk_info.sensors_count = sensors_count_from_rescan
        if not sensors_count_from_rescan:
            scan_info.trunks[trunk_number] = trunk_info
            continue

        temperatures_on_trunk = connection.get_temperature_of_sensors_on_trunk(trunk_number=trunk_number)
        for index, info in enumerate(temperatures_on_trunk):
            trunk_info.sensors_temperatures[index] = info.temperature

        addresses_on_trunk = connection.get_sensors_unique_address_on_trunk(trunk_number=trunk_number)
        for index, info in enumerate(addresses_on_trunk):
            trunk_info.sensors_addresses[index] = info.address

        scan_info.trunks[trunk_number] = trunk_info

    return ScanResults(
        info=scan_info,
        time_elapsed=shared.timedelta_from_monotonic_time(timestamp_begin)
    )


def check_that_can_reconfigure_address(connection: controller_communicator.VrcT70Communicator):
    saved_address = connection.address

    test_address = (saved_address + 1) % 256
    test_address = test_address if test_address else 1
    logger.debug(f"Will try to apply new test address {test_address}")
    connection.set_controller_new_address(new_controller_address=test_address)

    logger.debug("Checking that controller is accessible with new address")
    connection.address = test_address
    connection.ping()

    connection.set_controller_new_address(new_controller_address=saved_address)
    logger.debug("Checking that controller is accessible with old address")


def print_scan_results(results: ScanResults):
    scan_time = humanize.precisedelta(
        results.time_elapsed,
        minimum_unit="milliseconds", format="%0.2f"
    )

    info = results.info
    logger.info(
        f"Scan finished for controller 0x{info.address:02x} with session id 0x{info.session_id:04x} in {scan_time}"
    )

    header = ["Trunk", "Sensor index", "Sensor address", "Temperature"]
    table_data = [header]

    for trunk_number in shared.trunks_indexes():
        trunk_info = info.trunks[trunk_number]
        sensors_index = []
        sensors_address = []
        sensors_temperature = []

        for sensor_index in range(trunk_info.sensors_count):
            sensors_index.append(str(sensor_index))
            sensors_address.append(f"{trunk_info.sensors_addresses[sensor_index]:08x}")
            sensors_temperature.append(f"{trunk_info.sensors_temperatures[sensor_index]:0.2f}")

        sensors_index = "\n".join(sensors_index) if sensors_index else "N/A"
        sensors_address = "\n".join(sensors_address) if sensors_address else "N/A"
        sensors_temperature = "\n".join(sensors_temperature) if sensors_temperature else "N/A"
        table_data.append(
            [
                int(trunk_number),
                sensors_index,
                sensors_address,
                sensors_temperature,
            ]
        )
        # for sensor_index in range(trunk_info.sensors_count):

    table = terminaltables.AsciiTable(table_data=table_data)
    logger.info(f"Scan results:\n{table.table}")


@click.command(
    name="demo-app-1",
    context_settings=dict(ignore_unknown_options=True, allow_extra_args=True),
    add_help_option=False
)
@click.argument("additional_args", nargs=-1, type=click.UNPROCESSED)
def demo_app_1(additional_args):
    arg_parser = basic_arg_parser.create_basic_parser_for_single_controller()
    args = arg_parser.parse_args(additional_args)

    cli_shared.setup_logging()
    logger.info("Connecting to controller")

    uart = None
    try:
        logger.info("Opening port ...")
        uart = shared.init_serial(args.port, args.baudrate, args.timeout)

        connection = controller_communicator.VrcT70Communicator(
            port=uart,
            address=args.address
        )

        connection.ping()
        logger.info("Performing test to check if can reconfigure controller address")
        # check_that_can_reconfigure_address(connection=connection)

        # Retrieving all information using sequential operations
        sequential_results = sequential_scan(
            connection=connection,
            address=args.address
        )
        sequential_scan_time_human_readable = humanize.precisedelta(
            sequential_results.time_elapsed,
            minimum_unit="milliseconds", format="%0.2f"
        )

        # Performing batched scan
        batched_results = batched_scan(
            connection=connection,
            address=args.address
        )
        batched_scan_time_human_readable = humanize.precisedelta(
            batched_results.time_elapsed,
            minimum_unit="milliseconds", format="%0.2f"
        )

        logger.info(f"Sequential scan is finished in {sequential_scan_time_human_readable}")
        logger.info(f"Device info: {sequential_results.info}")
        print_scan_results(sequential_results)

        logger.info(f"Batched scan is finished in {batched_scan_time_human_readable}")
        logger.info(f"Device info: {batched_results.info}")
        print_scan_results(batched_results)

    finally:
        if uart:
            logger.info("Closing UART")
            uart.close()
