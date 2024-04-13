import logging

import terminaltables

from vrc_t70 import controller_manager

logger = logging.getLogger(__name__)


class EventsHandler(controller_manager.VrcT70ManagerEventsHandler):
    def controller_connected(self, controller_address: int) -> None:
        logger.info(f"Controller connected, address {controller_address}")

    def controller_disconnected(self, controller_address: int) -> None:
        logger.error(f"Controller is disconnected, address {controller_address}")

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

    def temperature_of_sensors_received(
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
