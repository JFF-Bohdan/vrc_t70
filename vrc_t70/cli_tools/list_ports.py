import click

from loguru import logger

import serial.tools.list_ports

import terminaltables


@click.command(
    name="list-ports",
    context_settings=dict(ignore_unknown_options=True, allow_extra_args=True),
    add_help_option=False,
)
def list_ports():
    logger.info("Looking for available COM ports ...")

    ports = serial.tools.list_ports.comports()
    if not ports:
        logger.warning("No COM ports has been found")
        return

    logger.info(f"Found {len(ports)} port(s)")

    data = [
        ("#", "Name", "Device name", "VID", "PID", "Serial number", "Manufacturer", "Description")
    ]

    for index, port in enumerate(ports):
        data.append(
            [
                index,
                port.name,
                port.device,
                port.vid,
                port.pid,
                port.serial_number,
                port.manufacturer,
                port.description
            ]
        )

    table = terminaltables.AsciiTable(data)
    logger.info(f"Available devices:\n{table.table}")
