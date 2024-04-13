import click

from vrc_t70.cli_tools.demo_app_1 import demo_app_1
from vrc_t70.cli_tools.demo_app_2 import demo_app_2
from vrc_t70.cli_tools.demo_app_3 import demo_app_3
from vrc_t70.cli_tools.find_controllers import find_controllers
from vrc_t70.cli_tools.list_ports import list_ports


@click.group()
def cli():
    pass  # pragma: no coverage


cli.add_command(list_ports)
cli.add_command(find_controllers)
cli.add_command(demo_app_1)
cli.add_command(demo_app_2)
cli.add_command(demo_app_3)
