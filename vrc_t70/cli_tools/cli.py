import click

from vrc_t70.cli_tools.list_ports import list_ports


@click.group()
def cli():
    pass


cli.add_command(list_ports)
