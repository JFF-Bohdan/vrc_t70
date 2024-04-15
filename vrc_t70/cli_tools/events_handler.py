import collections
import logging
import os

from vrc_t70 import controller_manager
from vrc_t70.cli_tools import shared as cli_shared

logger = logging.getLogger(__name__)


class EventsHandler(controller_manager.VrcT70ManagerEventsHandler):
    def __init__(self):
        self.is_connected: dict[int, bool] = collections.defaultdict(bool)
        self.info: dict[int, cli_shared.VrcT70DeviceInfo] = collections.defaultdict(cli_shared.VrcT70DeviceInfo)

    def controller_connected(self, controller_address: int) -> None:
        self.is_connected[controller_address] = True
        self._print(controller_address)

    def controller_disconnected(self, controller_address: int) -> None:
        self.is_connected[controller_address] = True
        self._print(controller_address)

    def number_of_sensors_on_trunk_received(
            self,
            controller_address: int,
            trunk_number: int,
            sensors_count: int
    ) -> None:
        info = self.info[controller_address]
        info.trunks[trunk_number].sensors_count = sensors_count
        self._print(controller_address)

    def address_of_sensors_received_on_trunk(
            self,
            controller_address: int,
            trunk_number: int,
            addresses: list[int | None],
    ):
        info = self.info[controller_address]

        for index, address in enumerate(addresses):
            info.trunks[trunk_number].sensors_addresses[index] = address

        self._print(controller_address)

    def temperature_of_sensors_received(
            self,
            controller_address: int,
            trunk_number: int,
            temperatures: list[float | None],
    ):
        info = self.info[controller_address]

        for index, temperature in enumerate(temperatures):
            info.trunks[trunk_number].sensors_temperatures[index] = temperature

        self._print(controller_address)

    def _print(self, controller_address: int):
        is_connected = self.is_connected[controller_address]
        info = self.info[controller_address]
        os.system("cls" if os.name == "nt" else "clear")

        print(f"Controller connected : {is_connected}")
        print(f"Controller address   : {controller_address}")

        report = cli_shared.print_scan_info(info)
        print(report)
        print()
        print("Press Ctrl-C to terminate program...")
