import datetime
import random
import time

from vrc_t70.sample_shared.models.devices import VrcT70Device
from vrc_t70.sample_shared.models.sensors import VrcT70Sensor

from .utils import hexlify_to_string
from .vrc_t70_stateful_communicator import VrcT70StatefulCommunicator


class VrcT70Daemon(object):
    DEFAULT_POLLING_SLEEP_INTERVAL = 1

    def __init__(self, serial, devices_addresses, logger, db_session):
        self._serial = serial
        self._devices_addresses = devices_addresses
        self._communicators = []
        self.logger = logger
        self._stop = False
        self._polling_sleep_interval = VrcT70Daemon.DEFAULT_POLLING_SLEEP_INTERVAL
        self.db_session = db_session

        self._map_device_addresses_to_ids = dict()
        self._round_precission = 3

    def init(self):
        for device_address in self._devices_addresses:
            hex_device_address = "0x{0:02x}".format(device_address)
            self.logger.info("creating new communicator for device {}".format(hex_device_address))

            communicator = VrcT70StatefulCommunicator(self._serial, controller_address=device_address, logger=self.logger)
            communicator.ping()

            new_session_id = random_byte_array(4)
            self.logger.debug("initializing session id with {}".format(hexlify_to_string(new_session_id)))
            r = communicator.set_session_id(new_session_id)
            assert r.session_id() == new_session_id

            self.logger.debug("scanning for sensors on trunks...")
            communicator.rescan_sensors_on_trunks()

            self.logger.info(
                "sensors count per trunk for {}: {}".format(
                    hex_device_address,
                    communicator.get_sensors_per_trunk_count()
                )
            )
            self._communicators.append(communicator)
            self._on_communicator_registration(communicator)

    def run(self):
        while not self._stop:
            for communicator in self._communicators:
                if self._stop:
                    break

                self.logger.info("updating data for controller {}".format(communicator.hex_device_address_for_communicator()))
                events = communicator.update_temperatures()
                self.logger.info("events: {}".format(events))

                self._on_events_from_device_received(communicator, events)

            if self._stop:
                break

            self.logger.debug("going to sleep for {} second(s)".format(self._polling_sleep_interval))
            time.sleep(self._polling_sleep_interval)

    def stop(self):
        self._stop = True

    def _on_events_from_device_received(self, communicator, events):
        device_id = self._map_device_addresses_to_ids[communicator.controller_address]

        for event in events:
            sensor = self.db_session.query(
                VrcT70Sensor
            ).filter(
                VrcT70Sensor.device_id == device_id,
                VrcT70Sensor.sensor_address == event.sensor_address
            ).scalar()

            new_sensor = False
            if not sensor:
                sensor = VrcT70Sensor()
                sensor.device_id = device_id
                sensor.sensor_address = event.sensor_address
                new_sensor = True

            sensor.trunk_number = event.trunk_number
            sensor.sensor_index = event.sensor_index
            sensor.is_connected = event.is_connected
            sensor.temperature = round(event.temperature, self._round_precission) \
                if event.temperature is not None else None

            if new_sensor:
                self.db_session.add(sensor)

        self.db_session.commit()

    def _on_communicator_registration(self, communicator):
        vrc_t70_device = self.db_session.query(
            VrcT70Device
        ).filter(
            VrcT70Device.device_address == communicator.controller_address
        ).scalar()

        if vrc_t70_device:
            vrc_t70_device.last_update_timestamp = utc_now()
            self._map_device_addresses_to_ids[communicator.controller_address] = vrc_t70_device.device_id

            self.db_session.query(
                VrcT70Sensor
            ).filter(
                VrcT70Sensor.device_id == vrc_t70_device.device_id
            ).delete(synchronize_session=False)

            self.db_session.commit()
            return

        vrc_t70_device = VrcT70Device()

        vrc_t70_device.device_address = communicator.controller_address
        vrc_t70_device.device_name = "Device {}".format(communicator.hex_device_address_for_communicator())
        self.db_session.add(vrc_t70_device)
        self.db_session.flush()
        self._map_device_addresses_to_ids[vrc_t70_device.device_id] = communicator.controller_address

        self.db_session.commit()


def random_byte_array(length):
    return bytearray((random.getrandbits(8) for _ in range(length)))


def utc_now():
    return datetime.datetime.utcnow()
