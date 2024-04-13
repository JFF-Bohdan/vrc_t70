import configargparse

from vrc_t70 import defaults


def create_basic_parser_no_ports(auto_env_var_prefix=None) -> configargparse.ArgumentParser:
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
        "-s",
        "--baudrate",
        action="store",
        help="UART port baudrate",
        type=int,
        default=defaults.DEFAULT_PORT_SPEED
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
        "-t",
        "--timeout",
        action="store",
        type=int,
        help="UART timeout",
        default=defaults.DEFAULT_TIMEOUT
    )

    return parser


def create_basic_parser_for_single_controller(auto_env_var_prefix=None) -> configargparse.ArgumentParser:
    parser = create_basic_parser_no_ports(auto_env_var_prefix=auto_env_var_prefix)

    parser.add_argument(
        "-a",
        "--address",
        action="store",
        help="Device address",
        type=int,
        default=defaults.DEFAULT_CONTROLLER_ADDRESS
    )

    return parser


def create_basic_parser_for_multiple_controllers(auto_env_var_prefix=None) -> configargparse.ArgumentParser:
    parser = create_basic_parser_no_ports(auto_env_var_prefix=auto_env_var_prefix)
    parser.add_argument(
        "-a",
        "--addresses",
        action="append",
        help="Device address",
        type=int,
        default=defaults.DEFAULT_CONTROLLER_ADDRESS
    )

    return parser
