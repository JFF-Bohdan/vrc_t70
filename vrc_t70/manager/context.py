import collections
import queue
import typing

from vrc_t70 import shared


class VrcT70ManagerContext:
    def __init__(self, max_queue_size: int = 0):
        self.tasks_queue = queue.PriorityQueue(maxsize=max_queue_size)
        self.last_communication_time: typing.Optional[float] = None
        self.session_id: typing.Optional[int] = None

        # How many times we had no response from controller
        self.no_response_count = 0

        self.expected_sensors_count_on_trunk: dict[int, int] = {}
        self.addresses_on_trunk: collections.defaultdict[int, list[int | None]] = \
            collections.defaultdict(shared.list_of_nones_for_trunk)
        self.temperatures_on_trunk: collections.defaultdict[int, list[float | None]] = \
            collections.defaultdict(shared.list_of_nones_for_trunk)

        # Full information about sensor (mapping sensor address to full information available about it)
        self.full_sensor_info: dict[int, shared.FullSensorInfo] = {}

        # Stores time when last time temperature on trunk has been received
        self.timestamp_temperature_refresh_on_trunk: dict[int, float] = collections.defaultdict(int)

    def clear_data_retrieved_from_controller(self):
        self.expected_sensors_count_on_trunk.clear()
        self.addresses_on_trunk.clear()
        self.temperatures_on_trunk.clear()
        self.timestamp_temperature_refresh_on_trunk.clear()
        self.full_sensor_info.clear()

    def has_data_for_all_trunks(self) -> bool:
        """
        Returns true when we have addresses and temperatures for all trunks
        """
        addresses_on_trunk = set(self.addresses_on_trunk.keys())
        temperatures_on_trunk = set(self.temperatures_on_trunk.keys())
        expected_trunks = set(shared.trunks_indexes())

        return (addresses_on_trunk == expected_trunks) and (temperatures_on_trunk == expected_trunks)
