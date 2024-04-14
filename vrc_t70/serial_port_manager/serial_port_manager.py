import logging
import time
import typing

import serial

from vrc_t70 import controller_manager

logger = logging.getLogger(__name__)


class SerialPortManager:
    DEFAULT_SLEEP_INTERVAL_ON_SERIAL_PORT_ERROR = 5
    DEFAULT_REOPEN_ATTEMPTS_COUNT_BEFORE_CREATING_NEW_PORT = 2

    def __init__(
        self,
        port_opener: typing.Callable,
        managers_for_controllers: list[controller_manager.VrcT70Manager],
        sleep_interval_on_error: typing.Optional[float] = DEFAULT_SLEEP_INTERVAL_ON_SERIAL_PORT_ERROR,
        reopen_attempts_count_before_creating_new_port: int = DEFAULT_REOPEN_ATTEMPTS_COUNT_BEFORE_CREATING_NEW_PORT,
    ):
        self.port_opener = port_opener
        self.managers_for_controllers = managers_for_controllers
        self.reopen_attempts_count_before_creating_new_port = reopen_attempts_count_before_creating_new_port
        self.sleep_interval_on_error = sleep_interval_on_error
        self._uart: typing.Optional[serial.Serial] = None

        self._errors_count = 0

    def communicate(
            self,
            max_time_to_talk: typing.Optional[float] = None,
    ):
        try:
            if (self._uart is None) or self._uart.closed:
                self._open_port()

                for manager in self.managers_for_controllers:
                    manager.communicator.port = self._uart

            max_time_to_talk_per_controller = max_time_to_talk / len(self.managers_for_controllers) \
                if max_time_to_talk else None
            for manager in self.managers_for_controllers:
                manager.communicate(max_time_to_talk=max_time_to_talk_per_controller)

        except serial.SerialException as e:
            self._errors_count += 1
            logger.error(f"Error communicating via serial port: {e}")

            logger.info("Closing port")
            self.close()

            if (
                (self.reopen_attempts_count_before_creating_new_port is not None) and
                (self._errors_count >= self.reopen_attempts_count_before_creating_new_port)
            ):
                logger.warning("Got too many errors, destroying serial port connection...")
                self._errors_count = 0
                self._uart = None

            if self.sleep_interval_on_error:
                logger.info(f"Going to sleep for {self.sleep_interval_on_error} second(s)...")
                time.sleep(self.sleep_interval_on_error)

    def close(self):
        if not self._uart:
            logger.info("Serial port is not opened, skipping operation")
            return

        if self._uart.closed:
            logger.info("Port is already closed, skipping operation")
            return

        try:
            self._uart.close()
        except serial.SerialException as e:
            logger.warning(f"Problem during port closing (ignorign it): {e}")

    def _open_port(self):
        logger.info("Trying to open serial port")
        self._uart = self.port_opener()
        logger.info("Serial port successfully opened")
