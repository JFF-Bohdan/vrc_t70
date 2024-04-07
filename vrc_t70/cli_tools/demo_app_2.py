import threading
import time

import click

from loguru import logger

import terminaltables

from vrc_t70 import shared
from vrc_t70.cli_tools import basic_arg_parser
from vrc_t70.cli_tools import shared as cli_shared
from vrc_t70.communicator import communicator
from vrc_t70.communicator import controller_manager


class EventsHandler(controller_manager.VrcT70ManagerEventsHandler):
    def controller_connected(self, controller_address: int) -> None:
        logger.info(f"Controller connected, address {controller_address}")

    def controller_disconnected(self, controller_address: int) -> None:
        logger.warning(f"Controller is disconnected, address {controller_address}")

    def number_of_sensors_on_trunk_received(
            self,
            controller_address: int,
            trunk_number: int,
            sensors_count: int
    ) -> None:
        logger.info(f"Number of sensors on trunk received. Trunk {trunk_number}, number of sensors {sensors_count}")

    def address_of_sensors_received_on_trunk(
            self,
            controller_address: int,
            trunk_number: int,
            addresses: list[int | None],
    ):
        data = [
            ["Sensor index", "Address"]
        ]
        for index, address in enumerate(addresses):
            data.append(
                [
                    index,
                    f"0x{address:08x}" if address else "N/A"
                ]
            )

        table = terminaltables.AsciiTable(data)
        logger.info(f"Address of sensors on trunk received. Trunk {trunk_number}, addresses:\n{table.table}")

    def temperature_of_sensor_received(
            self,
            controller_address: int,
            trunk_number: int,
            temperatures: list[float | None],
    ):
        data = [
            ["Sensor index", "Temperature"]
        ]
        for index, temperature in enumerate(temperatures):
            data.append(
                [
                    index,
                    f"{temperature:0.2f}" if temperature else "N/A"
                ]
            )

        table = terminaltables.AsciiTable(data)
        logger.info(f"Temperature of sensors on trunk received. Trunk {trunk_number}, temperatures:\n{table.table}")


@click.command(
    name="demo-app-2",
    context_settings=dict(ignore_unknown_options=True, allow_extra_args=True),
    add_help_option=False
)
@click.argument("additional_args", nargs=-1, type=click.UNPROCESSED)
def demo_app_2(additional_args):
    arg_parser = basic_arg_parser.create_basic_parser()
    args = arg_parser.parse_args(additional_args)
    logger.info("Searching for controllers")

    stop_event = threading.Event()
    cli_shared.register_interception_of_ctrl_c("Termination requested...", stop_event)

    uart = None
    try:
        logger.info("Opening port ...")
        uart = shared.init_serial(args.port, args.baudrate, args.timeout)

        manager = controller_manager.VrcT70Manager(
            communicator=communicator.VrcT70Communicator(
                port=uart,
                address=args.address
            ),
            options=controller_manager.VrcT70ManagerOptions(),
            events_handler=EventsHandler()
        )

        while True:
            manager.communicate(max_time_to_talk=1.0)
            if stop_event.is_set():
                logger.info("Exiting...")
                break
            time.sleep(0.5)

    finally:
        if uart:
            logger.info("Closing UART")
            uart.close()
