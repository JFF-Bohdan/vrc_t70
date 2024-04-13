import logging
import threading
import time

import click

from vrc_t70 import controller_communicator, controller_manager, shared
from vrc_t70.cli_tools import basic_arg_parser
from vrc_t70.cli_tools import events_handler
from vrc_t70.cli_tools import shared as cli_shared


logger = logging.getLogger(__name__)


@click.command(
    name="demo-app-2",
    context_settings=dict(ignore_unknown_options=True, allow_extra_args=True),
    add_help_option=False
)
@click.argument("additional_args", nargs=-1, type=click.UNPROCESSED)
def demo_app_2(additional_args):
    arg_parser = basic_arg_parser.create_basic_parser_for_single_controller()
    args = arg_parser.parse_args(additional_args)

    cli_shared.setup_logging()
    logger.info("Connecting to controller")

    stop_event = threading.Event()
    cli_shared.register_interception_of_ctrl_c("Termination requested...", stop_event)

    uart = None
    try:
        logger.info("Opening port ...")
        uart = shared.init_serial(args.port, args.baudrate, args.timeout)

        manager = controller_manager.VrcT70Manager(
            communicator=controller_communicator.VrcT70Communicator(
                port=uart,
                address=args.address
            ),
            options=controller_manager.VrcT70ManagerOptions(),
            events_handler=events_handler.EventsHandler()
        )

        while True:
            manager.communicate(max_time_to_talk=1.0)
            if stop_event.is_set():
                logger.info("Exiting...")
                break
            time.sleep(0.5)
    except Exception:
        logger.exception("Error communicating")
        raise
    finally:
        if uart:
            logger.info("Closing UART")
            uart.close()

    logger.info("Application finished")
