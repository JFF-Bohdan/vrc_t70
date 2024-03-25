import click

from vrc_t70.cli_tools.demo_app import demo_app
from vrc_t70.cli_tools.find_controllers import find_controllers
from vrc_t70.cli_tools.list_ports import list_ports


@click.group()
def cli():
    pass  # pragma: no coverage


cli.add_command(list_ports)
cli.add_command(find_controllers)
cli.add_command(demo_app)
