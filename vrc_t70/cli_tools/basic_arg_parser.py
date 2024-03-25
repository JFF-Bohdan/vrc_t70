import configargparse

from vrc_t70 import defaults


def create_basic_parser(auto_env_var_prefix=None) -> configargparse.ArgumentParser:
    parser = configargparse.ArgParser(
        auto_env_var_prefix=auto_env_var_prefix
    )

    parser.add_argument(
        "--config",
        metavar="FILE",
        is_config_file=True,
        help="Path to configuration file",
        required=False
    )

    parser.add_argument(
        "-p",
        "--port",
        action="store",
        type=str,
        help="Name of UART port",
        required=True
    )

    parser.add_argument(
        "-s",
        "--speed",
        action="store",
        help="UART port speed",
        type=int,
        default=defaults.DEFAULT_PORT_SPEED
    )

    parser.add_argument(
        "-a",
        "--address",
        action="store",
        help="Device address",
        type=int,
        default=defaults.DEFAULT_CONTROLLER_ADDRESS
    )

    parser.add_argument(
        "-t",
        "--timeout",
        action="store",
        type=int,
        help="UART timeout",
        default=None
    )

    return parser
