import functools
import logging
import threading
import time

import click

from vrc_t70 import controller_communicator, controller_manager, serial_port_manager, shared
from vrc_t70.cli_tools import basic_arg_parser
from vrc_t70.cli_tools import events_handler
from vrc_t70.cli_tools import shared as cli_shared


logger = logging.getLogger(__name__)


@click.command(
    name="demo-app-3",
    context_settings=dict(ignore_unknown_options=True, allow_extra_args=True),
    add_help_option=False
)
@click.argument("additional_args", nargs=-1, type=click.UNPROCESSED)
def demo_app_3(additional_args):
    arg_parser = basic_arg_parser.create_basic_parser_for_multiple_controllers()
    args = arg_parser.parse_args(additional_args)

    cli_shared.setup_logging()
    logger.info("Searching for controllers")

    stop_event = threading.Event()
    cli_shared.register_interception_of_ctrl_c("Termination requested...", stop_event)

    port_opener = functools.partial(
        shared.init_serial,
        port_name=args.port,
        baudrate=args.baudrate,
        timeout=args.timeout,
    )

    managers = []
    for address in args.addresses:
        managers.append(
            controller_manager.VrcT70Manager(
                communicator=controller_communicator.VrcT70Communicator(
                    port=None,
                    address=address
                ),
                options=controller_manager.VrcT70ManagerOptions(),
                events_handler=events_handler.EventsHandler()
            )
        )

    port_manager = serial_port_manager.SerialPortManager(port_opener=port_opener, managers_for_controllers=managers)

    try:
        while True:
            port_manager.communicate(max_time_to_talk=1.0)

            if stop_event.is_set():
                logger.info("Exiting...")
                break

                # manager.VrcT70Manager

            time.sleep(0.5)

    finally:
        port_manager.close()
        logger.info("Closing UART")

    logger.info("Application finished")
