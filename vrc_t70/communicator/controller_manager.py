import collections
import dataclasses
import enum
import functools
import queue
import random
import time
import typing

from loguru import logger

from vrc_t70 import exceptions
from vrc_t70 import limitations
from vrc_t70 import shared
from vrc_t70.communicator import communicator
from vrc_t70.protocol.requests import ping_request

DEFAULT_INTERVAL_FOR_TEMPERATURE_REFRESH = 10
INTERVAL_FOR_PING_REQUESTS = 5
DEFAULT_MAX_MISSED_COMMUNICATIONS = 6


class VrcT70ManagerTaskPriority(enum.IntEnum):
    HIGH = 0
    MEDIUM = 5
    LOW = 10
    ULTRA_LOW = 50


@dataclasses.dataclass(order=True)
class VrcT70ManagerTask:
    priority: int
    task: typing.Callable = dataclasses.field(compare=False)
    additional_sort_attribute: int = 0


@dataclasses.dataclass
class VrcT70ManagerOptions:
    interval_between_pings: float = INTERVAL_FOR_PING_REQUESTS
    interval_between_temperature_refresh: float = DEFAULT_INTERVAL_FOR_TEMPERATURE_REFRESH
    missed_communications_before_disconnect: int = DEFAULT_MAX_MISSED_COMMUNICATIONS


class VrcT70ManagerContext:
    def __init__(self, max_queue_size: int = 0):
        self.tasks_queue = queue.PriorityQueue(maxsize=max_queue_size)
        self.last_communication_time: typing.Optional[float] = None
        self.session_id: typing.Optional[int] = None

        # How many times we had no response from controller
        self.no_response_count = 0

        self.expected_sensors_count_on_trunk: dict[int, int] = {}
        self.addresses_on_trunk: collections.defaultdict[int, list[int | None]] = collections.defaultdict(list)
        self.temperatures_on_trunk: collections.defaultdict[int, list[float | None]] = collections.defaultdict(list)

        # Mapping from sensor address to temperature
        self.temperatures_on_sensors: dict[int, float] = {}

        # Stores time when last time temperature on trunk has been received
        self.timestamp_temperature_refresh_on_trunk: dict[int, float] = collections.defaultdict(int)

    def clear_data_retrieved_from_controller(self):
        self.expected_sensors_count_on_trunk.clear()
        self.addresses_on_trunk.clear()
        self.temperatures_on_trunk.clear()
        self.temperatures_on_sensors.clear()
        self.timestamp_temperature_refresh_on_trunk.clear()

    def has_data_for_all_trunks(self) -> bool:
        """
        Returns true when we have addresses and temperatures for all trunks
        """
        addresses_on_trunk = set(self.addresses_on_trunk.keys())
        temperatures_on_trunk = set(self.temperatures_on_trunk.keys())
        available_trunks = set(shared.trunks_indexes())

        return (addresses_on_trunk == available_trunks) and (temperatures_on_trunk == available_trunks)


class VrcT70ManagerEventsHandler:
    def controller_connected(self, controller_address: int) -> None:
        pass

    def controller_disconnected(self, controller_address: int) -> None:
        pass

    def number_of_sensors_on_trunk_received(
            self,
            controller_address: int,
            trunk_number: int,
            sensors_count: int
    ) -> None:
        pass

    def address_of_sensors_received_on_trunk(
            self,
            controller_address: int,
            trunk_number: int,
            addresses: list[int | None],
    ):
        pass

    def temperature_of_sensor_received(
            self,
            controller_address: int,
            trunk_number: int,
            temperatures: list[float | None],
    ):
        pass


def get_random_session_id(forbidden_value: typing.Optional[int] = None) -> int:
    """
    Returns non-zero session id. If forbidden_value is provided,
    will return value which is different from it
    """

    while True:
        result = random.getrandbits(32)
        if not result:
            continue

        if forbidden_value and (result == forbidden_value):
            continue

        break

    return result


class VrcT70Manager:
    def __init__(
            self,
            communicator: communicator.VrcT70Communicator,
            options: VrcT70ManagerOptions,
            events_handler: VrcT70ManagerEventsHandler
    ):
        self.communicator = communicator
        self.communicator.validate_sequence_id = False
        self.options = options
        self.events_handler = events_handler
        self.context = VrcT70ManagerContext()

    def communicate(self, max_time_to_talk: typing.Optional[float] = None):
        self._add_tasks()

        timestamp_begin = time.monotonic()
        while not self.context.tasks_queue.empty():
            try:
                logger.debug("Looking for new tasks...")
                task = self.context.tasks_queue.get(block=False)

                old_last_communication_time = self.context.last_communication_time
                self._process_task(task)
                self.context.last_communication_time = time.monotonic()
                self.context.no_response_count = 0

                if not old_last_communication_time:
                    self.events_handler.controller_connected(controller_address=self.communicator.address)

                # Checking if we still have time to process other tasks
                if max_time_to_talk and (time.monotonic() - timestamp_begin >= max_time_to_talk):
                    logger.info("No more time to talk, exiting...")
                    break
            except exceptions.ErrorNoResponseFromController:
                self.context.no_response_count += 1
                if self.context.no_response_count == self.options.missed_communications_before_disconnect:
                    self.context.last_communication_time = None
                    self.events_handler.controller_connected(self.communicator.address)

        logger.debug("No tasks to process, exiting...")

    def _process_task(self, task: VrcT70ManagerTask) -> None:
        """
        Processes task, returns True if communication was successful from protocol point of view,
        basically if we received something
        """
        task.task()

    def _add_tasks(self):
        # If we didn't talk for a long time, we would like check session id
        if (not self.context.last_communication_time) or (not self.context.session_id):
            logger.debug("Need to set new session id, clearing tasks queue")
            self.context.tasks_queue.queue.clear()
            self.context.tasks_queue.put(
                VrcT70ManagerTask(
                    priority=VrcT70ManagerTaskPriority.HIGH,
                    task=self._set_session_id_task
                )
            )
            return

        if self.context.has_data_for_all_trunks():
            refresh_requests_added_count = 0
            for trunk_number in shared.trunks_indexes():
                if not self._need_refresh_temperature_on_trunk(trunk_number):
                    continue

                self.context.tasks_queue.put(
                    VrcT70ManagerTask(
                        priority=VrcT70ManagerTaskPriority.LOW,
                        task=functools.partial(self._get_sensors_temperature_on_trunk_task, trunk_number),
                        additional_sort_attribute=trunk_number,
                    )
                )

            if refresh_requests_added_count:
                return

        if (
                (not self.context.last_communication_time) or
                (time.monotonic() - self.context.last_communication_time) >= self.options.interval_between_pings
        ):
            self.context.tasks_queue.put(
                VrcT70ManagerTask(
                    priority=VrcT70ManagerTaskPriority.ULTRA_LOW,
                    task=self._ping_task,
                )
            )

    def _set_session_id_task(self) -> None:
        """
        Sets communication session with controller. When it's performed we assume that we just
        started communication with controller and need to rescan all trunks and get current state of:

        - information about all connected sensors
        - temperature on all sensors

        As a result, before performing operation we are going to clear all already known information.
        """
        self.context.clear_data_retrieved_from_controller()

        logger.debug("Applying new session id")
        new_session_id = self.communicator.set_session_id(get_random_session_id(self.context.session_id))
        self.context.session_id = new_session_id

        for trunk_number in shared.trunks_indexes():
            logger.debug(f"Adding task to rescan sensors on trunk {trunk_number}")
            self.context.tasks_queue.put(
                VrcT70ManagerTask(
                    priority=VrcT70ManagerTaskPriority.HIGH,
                    task=functools.partial(self._rescan_sensors_on_trunk_task, trunk_number),
                    additional_sort_attribute=trunk_number,
                )
            )

    def _rescan_sensors_on_trunk_task(self, trunk_number: int) -> None:
        sensors_count = self.communicator.rescan_sensors_on_trunk(trunk_number=trunk_number)
        logger.info(f"Found sensors count on trunk {trunk_number} is {sensors_count}")
        self.context.expected_sensors_count_on_trunk[trunk_number] = sensors_count

        self.context.tasks_queue.put(
            VrcT70ManagerTask(
                priority=VrcT70ManagerTaskPriority.MEDIUM,
                task=functools.partial(self._get_sensors_address_on_trunk_task, trunk_number),
                additional_sort_attribute=trunk_number,
            )
        )

        self.context.tasks_queue.put(
            VrcT70ManagerTask(
                priority=VrcT70ManagerTaskPriority.LOW,
                task=functools.partial(self._get_sensors_temperature_on_trunk_task, trunk_number),
                additional_sort_attribute=trunk_number,
            )
        )

        self.events_handler.number_of_sensors_on_trunk_received(
            controller_address=self.communicator.address,
            trunk_number=trunk_number,
            sensors_count=sensors_count
        )

    def _get_sensors_address_on_trunk_task(self, trunk_number: int):
        logger.debug(f"Querying sensors address on trunk {trunk_number}")
        response = self.communicator.get_sensors_unique_address_on_trunk(trunk_number=trunk_number)
        addresses = [None] * (limitations.MAX_SENSOR_INDEX + 1)
        for sensor_address in response:
            # TODO: need to be handled
            # sensor_address.is_error_detected
            addresses[sensor_address.sensor_index] = sensor_address.address

        self.context.addresses_on_trunk[trunk_number] = addresses

        self.events_handler.address_of_sensors_received_on_trunk(
            controller_address=self.communicator.address,
            trunk_number=trunk_number,
            addresses=addresses
        )

    def _get_sensors_temperature_on_trunk_task(self, trunk_number: int):
        logger.debug(f"Querying temperature of sensors on trunk {trunk_number}")
        response = self.communicator.get_temperature_of_sensors_on_trunk(trunk_number=trunk_number)
        temperatures = [None] * (limitations.MAX_SENSOR_INDEX + 1)
        for sensor_data in response:
            # TODO: need to be handled
            # sensor_data.is_connected
            temperatures[sensor_data.sensor_index] = sensor_data.temperature

            sensor_address = self.context.addresses_on_trunk[trunk_number][sensor_data.sensor_index]
            if sensor_address:
                self.context.temperatures_on_sensors[sensor_address] = sensor_data.temperature

        self.context.temperatures_on_trunk[trunk_number] = temperatures

        self.events_handler.temperature_of_sensor_received(
            controller_address=self.communicator.address,
            trunk_number=trunk_number,
            temperatures=temperatures
        )
        self.context.timestamp_temperature_refresh_on_trunk[trunk_number] = time.monotonic()

    def _ping_task(self):
        logger.debug("PING")
        self.communicator.communicate(ping_request.PingRequest())

    def _need_refresh_temperature_on_trunk(self, trunk_number: int) -> bool:
        """
        Returns true if it's time to refresh temperatures on trunk
        """
        last_request_time = self.context.timestamp_temperature_refresh_on_trunk[trunk_number]
        if not last_request_time:
            return True

        return (time.monotonic() - last_request_time) >= self.options.interval_between_temperature_refresh
