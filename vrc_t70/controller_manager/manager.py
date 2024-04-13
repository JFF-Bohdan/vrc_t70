import functools
import logging
import time
import typing

from vrc_t70 import controller_communicator, exceptions, shared
from vrc_t70.controller_manager import context, events_handler, misc, options, task_type


logger = logging.getLogger(__name__)


class VrcT70Manager:
    def __init__(
            self,
            communicator: controller_communicator.VrcT70Communicator,
            options: options.VrcT70ManagerOptions,
            events_handler: events_handler.VrcT70ManagerEventsHandler
    ):
        self.communicator = communicator
        self.communicator.validate_sequence_id = False
        self.options = options
        self.events_handler = events_handler
        self.context = context.VrcT70ManagerContext()

    def communicate(self, max_time_to_talk: typing.Optional[float] = None):
        """
        Communicates with VRC-T70 controller by choosing which commands to send depending on a current
        context - current known information about controller / trunks / available sensors, etc.

        TODO: add more information
        """
        self._add_tasks()

        timestamp_begin = time.monotonic()
        while not self.context.tasks_queue.empty():
            try:
                logger.debug(f"Looking for new tasks [Queue size {self.context.tasks_queue.qsize()}]...")

                old_last_communication_time = self.context.last_communication_time
                task = typing.cast(task_type.VrcT70ManagerTask, self.context.tasks_queue.get(block=False))
                task.task()

                self.context.last_communication_time = time.monotonic()
                self.context.no_response_count = 0

                if not old_last_communication_time:
                    self.events_handler.controller_connected(controller_address=self.communicator.address)

                # Checking if we still have time to process other tasks
                if max_time_to_talk and (time.monotonic() - timestamp_begin >= max_time_to_talk):
                    logger.info("No more time to talk, exiting...")
                    break

            except (exceptions.ErrorNoResponseFromController, exceptions.ErrorBaseVrcT70) as e:
                if not isinstance(e, exceptions.ErrorNoResponseFromController):
                    logger.warning(f"Got unexpected exception: {e}")

                self.context.no_response_count += 1
                if self.context.no_response_count == self.options.missed_communications_count_before_disconnect:
                    self.context.last_communication_time = None
                    self.events_handler.controller_disconnected(self.communicator.address)

        logger.debug("No more tasks to process, exiting...")

    def _add_tasks(self):
        """
        Adds tasks for further communication depending on current context - all the information known about
        controller / trunks / sensors, etc.
        """

        # If we didn't talk for a long time, or we have no session id,
        # then we should like set session id
        if (not self.context.last_communication_time) or (not self.context.session_id):
            logger.debug("Need to set new session id, clearing tasks queue")
            self.context.tasks_queue.queue.clear()
            self.context.tasks_queue.put(
                task_type.VrcT70ManagerTask(
                    priority=task_type.VrcT70ManagerTaskPriority.HIGH,
                    task=self._set_session_id_task
                )
            )
            return

        # If we have information about all trunks (addresses of sensors and temperatures),
        # we periodically need to query for temperatures on sensors
        if self.context.has_data_for_all_trunks():
            logger.debug("Checking if need request temperatures on trunk...")
            refresh_requests_added_count = 0
            for trunk_number in shared.trunks_indexes():
                if not self._need_refresh_temperature_on_trunk(trunk_number):
                    continue

                self.context.tasks_queue.put(
                    task_type.VrcT70ManagerTask(
                        priority=task_type.VrcT70ManagerTaskPriority.LOW,
                        task=functools.partial(self._get_sensors_temperature_on_trunk_task, trunk_number),
                        additional_sort_attribute=trunk_number,
                    )
                )
                refresh_requests_added_count += 1

            if refresh_requests_added_count:
                return
        else:
            logger.warning("Not all trunks are scanned can't request temperatures periodically")

        # If queue is empty but data for some trunk is missing, we need to retrieve addresses and temperatures
        if self.context.tasks_queue.empty() and (not self.context.has_data_for_all_trunks()):
            self._request_update_info_on_trunks()

            # If we sent something, then it's enough
            if not self.context.tasks_queue.empty():
                return

        # If we have nothing to request, and we didn't talk for a long time with controller
        # we would send PING request
        if self._need_to_send_ping_request():
            self.context.tasks_queue.put(
                task_type.VrcT70ManagerTask(
                    priority=task_type.VrcT70ManagerTaskPriority.ULTRA_LOW,
                    task=self._ping_task,
                )
            )

    def _request_update_info_on_trunks(self) -> None:
        """
        Requests missing information about trunks:

        - for trunks where we do not have any addresses and temperatures it would request rescan
        - for trunks where count of sensors is not equal to expected one it would request rescan
        - for trunks where we have no information about addresses it would request query for addresses
        - for trunks where we have no information about temperatures it would request query for temperatures
        """

        # Computing set with numbers of all possible trunks which can exists on device
        required_trunks = set(shared.trunks_indexes())

        # Calculating list of trunks for which we don't have information about sensor
        # addresses or number of addresses is not equal for a count received during
        # rescanning info
        trunks_with_missing_addresses = required_trunks - set(self.context.addresses_on_trunk.keys())
        for trunk_number in required_trunks:
            expected_sensors_count = self.context.expected_sensors_count_on_trunk.get(trunk_number)
            available_addresses_qty = sum([1 if item else 0 for item in self.context.addresses_on_trunk[trunk_number]])

            if (expected_sensors_count is None) or (expected_sensors_count != available_addresses_qty):
                trunks_with_missing_addresses.add(trunk_number)

        logger.debug(f"trunks_with_missing_addresses = {trunks_with_missing_addresses}")

        # Computing list of trunks for which we do not have information about temperatures
        trunks_with_missing_temperatures = required_trunks - set(self.context.temperatures_on_trunk.keys())
        logger.debug(f"trunks_with_missing_temperatures = {trunks_with_missing_temperatures}")

        # Calculating list of trunks for which we do not have information about addresses
        # and information about temperatures. For these trunks we would request full rescan.
        missing_all_info = trunks_with_missing_addresses & trunks_with_missing_temperatures
        logger.debug(f"missing_all_info = {missing_all_info}")

        for trunk_number in missing_all_info:
            self.context.tasks_queue.put(
                task_type.VrcT70ManagerTask(
                    priority=task_type.VrcT70ManagerTaskPriority.HIGH,
                    task=functools.partial(self._rescan_sensors_on_trunk_task, trunk_number),
                    additional_sort_attribute=trunk_number,
                )
            )

        # For those trunks where we do not have information about addresses we would request
        # rescan of addresses on such trunk
        trunks_with_missing_addresses -= missing_all_info
        for trunk_number in trunks_with_missing_addresses:
            self.context.tasks_queue.put(
                task_type.VrcT70ManagerTask(
                    priority=task_type.VrcT70ManagerTaskPriority.MEDIUM,
                    task=functools.partial(self._get_sensors_address_on_trunk_task, trunk_number),
                    additional_sort_attribute=trunk_number,
                )
            )

        # For those trunks where we do not have information about temperatures we would request
        # rescan of temperatures on such trunk
        trunks_with_missing_temperatures -= missing_all_info
        for trunk_number in trunks_with_missing_temperatures:
            self.context.tasks_queue.put(
                task_type.VrcT70ManagerTask(
                    priority=task_type.VrcT70ManagerTaskPriority.LOW,
                    task=functools.partial(self._get_sensors_temperature_on_trunk_task, trunk_number),
                    additional_sort_attribute=trunk_number,
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
        new_session_id = self.communicator.set_session_id(misc.get_random_session_id(self.context.session_id))
        self.context.session_id = new_session_id

        for trunk_number in shared.trunks_indexes():
            logger.debug(f"Adding task to rescan sensors on trunk {trunk_number}")
            self.context.tasks_queue.put(
                task_type.VrcT70ManagerTask(
                    priority=task_type.VrcT70ManagerTaskPriority.HIGH,
                    task=functools.partial(self._rescan_sensors_on_trunk_task, trunk_number),
                    additional_sort_attribute=trunk_number,
                )
            )

    def _rescan_sensors_on_trunk_task(self, trunk_number: int) -> None:
        """
        Performs rescan of sensors on trunk.

        Once it would be finished, it would request information about addresses and temperatures
        """

        sensors_count = self.communicator.rescan_sensors_on_trunk(trunk_number=trunk_number)
        logger.info(f"Found sensors count on trunk {trunk_number} is {sensors_count}")
        self.context.expected_sensors_count_on_trunk[trunk_number] = sensors_count

        self.context.tasks_queue.put(
            task_type.VrcT70ManagerTask(
                priority=task_type.VrcT70ManagerTaskPriority.MEDIUM,
                task=functools.partial(self._get_sensors_address_on_trunk_task, trunk_number),
                additional_sort_attribute=trunk_number,
            )
        )

        self.context.tasks_queue.put(
            task_type.VrcT70ManagerTask(
                priority=task_type.VrcT70ManagerTaskPriority.LOW,
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
        """
        Queries addresses of all sensors on trunk
        """
        logger.debug(f"Querying sensors address on trunk {trunk_number}")
        response = self.communicator.get_sensors_unique_address_on_trunk(trunk_number=trunk_number)
        addresses = shared.list_of_nones_for_trunk()
        for sensor_address in response:
            # TODO: need to be handled
            # sensor_address.is_error_detected
            addresses[sensor_address.sensor_index] = sensor_address.address

            full_sensor_info = self.context.full_sensor_info.get(sensor_address.address)
            if full_sensor_info:
                full_sensor_info.has_error = sensor_address.is_error_detected
            else:
                full_sensor_info = shared.FullSensorInfo(
                    trunk_number=trunk_number,
                    sensor_index=sensor_address.sensor_index,
                    address=sensor_address.address,
                    has_error=sensor_address.is_error_detected
                )
                self.context.full_sensor_info[sensor_address.address] = full_sensor_info

        self.context.addresses_on_trunk[trunk_number] = addresses

        self.events_handler.address_of_sensors_received_on_trunk(
            controller_address=self.communicator.address,
            trunk_number=trunk_number,
            addresses=addresses
        )

    def _get_sensors_temperature_on_trunk_task(self, trunk_number: int):
        """
        Queries temperatures of all sensors on a trunk
        """

        logger.debug(f"Querying temperature of sensors on trunk {trunk_number}")
        response = self.communicator.get_temperature_of_sensors_on_trunk(trunk_number=trunk_number)
        temperatures = shared.list_of_nones_for_trunk()
        for sensor_data in response:
            # TODO: need to be handled
            # sensor_data.is_connected
            temperatures[sensor_data.sensor_index] = sensor_data.temperature

            sensor_address = self.context.addresses_on_trunk[trunk_number][sensor_data.sensor_index]
            if sensor_address:
                full_sensor_info = self.context.full_sensor_info.get(sensor_address)
                full_sensor_info.temperature = sensor_data.temperature
                full_sensor_info.has_error = (not sensor_data.is_connected)

        self.context.temperatures_on_trunk[trunk_number] = temperatures

        self.events_handler.temperature_of_sensors_received(
            controller_address=self.communicator.address,
            trunk_number=trunk_number,
            temperatures=temperatures
        )
        self.context.timestamp_temperature_refresh_on_trunk[trunk_number] = time.monotonic()

    def _ping_task(self):
        """
        Performs ping request. Used when there is no need to send other request,
        but we still want to be sure that controller is available.
        """
        logger.debug("PING")
        self.communicator.ping()

    def _need_refresh_temperature_on_trunk(self, trunk_number: int) -> bool:
        """
        Returns true if it's time to refresh temperatures on a trunk
        """
        last_request_time = self.context.timestamp_temperature_refresh_on_trunk[trunk_number]
        if not last_request_time:
            return True

        return (time.monotonic() - last_request_time) >= self.options.interval_between_temperatures_refresh

    def _need_to_send_ping_request(self) -> bool:
        """
        If there is no requests to send in a queue, and we didn't send any requests for a long time,
        it's time to send a ping request.
        """
        return (
            (self.context.tasks_queue.empty()) and
            (
                (not self.context.last_communication_time) or
                (time.monotonic() - self.context.last_communication_time) >= self.options.interval_between_pings
            )
        )
