from vrc_t70 import MAX_TRUNKS_COUNT, VrcT70Communicator

from .data_types import SensorReadData
from .utils import hexlify_to_string


class VrcT70StatefulCommunicator(VrcT70Communicator):
    def __init__(self, serial, controller_address, logger):
        super().__init__(serial, controller_address)
        self._sensors_per_trunk_count = dict()
        self.logger = logger

        self._sensors_addresses_per_trunk = dict()
        self._map_sensor_address_to_trunk_number_and_index = dict()
        self._map_sensor_address_to_temperature = dict()
        self._map_trunk_number_and_index_to_sensor_address = dict()

    def rescan_sensors_on_trunks(self):
        self._sensors_addresses_per_trunk = dict()
        self._map_sensor_address_to_trunk_number_and_index = dict()
        self._map_sensor_address_to_temperature = dict()
        self._map_trunk_number_and_index_to_sensor_address = dict()

        hex_device_address = self.hex_device_address_for_communicator()
        self.logger.info("rescanning devices on trunks for {}".format(hex_device_address))

        for trunk_number in range(1, MAX_TRUNKS_COUNT + 1):
            self.logger.info("scanning trunk {} for {}".format(trunk_number, hex_device_address))

            self.logger.debug("rescanning trunk")
            res = self.rescan_sensors_on_trunk(trunk_number)
            assert res.trunk_number() == trunk_number
            sensors_count = res.sensors_count()
            self._sensors_per_trunk_count[trunk_number] = sensors_count

            self.logger.info("retrieving sensors addresses")
            addresses = self.get_sensors_unique_addresses_on_trunk(trunk_number)
            assert sensors_count == addresses.sensors_count()

            addresses_on_trunk = []
            for sensor_index in range(sensors_count):
                assert not addresses.is_error_detected(sensor_index)
                unique_address = addresses.sensor_unique_address(sensor_index)
                unique_address = hexlify_to_string(unique_address)
                addresses_on_trunk.append(unique_address)

                sensor_position = (trunk_number, sensor_index)
                self._map_sensor_address_to_trunk_number_and_index[unique_address] = sensor_position
                self._map_trunk_number_and_index_to_sensor_address[sensor_position] = unique_address

            self._sensors_addresses_per_trunk[trunk_number] = addresses_on_trunk
            self.logger.info(
                "sensors addresses for trunk {}: {}".format(
                    trunk_number,
                    self.get_sensors_addresses_on_trunk(trunk_number)
                )
            )

        return self.get_sensors_per_trunk_count()

    def update_temperatures(self):
        updated_data = []

        for trunk_number in range(1, MAX_TRUNKS_COUNT + 1):
            sensors_count = self._sensors_per_trunk_count[trunk_number]

            temperatures = self.get_temperature_on_trunk(trunk_number)
            assert temperatures.temperatures_count() == sensors_count

            for sensor_index in range(sensors_count):
                is_connected = temperatures.is_connected(sensor_index)
                if is_connected:
                    temperature = temperatures.temperature(sensor_index)
                else:
                    temperature = None

                sensor_position = (trunk_number, sensor_index)
                unique_address = self._map_trunk_number_and_index_to_sensor_address[sensor_position]

                self._map_sensor_address_to_temperature[unique_address] = temperature

                event = SensorReadData(
                    device_address=self.controller_address,
                    sensor_address=unique_address,
                    trunk_number=trunk_number,
                    sensor_index=sensor_index,
                    is_connected=is_connected,
                    temperature=temperature
                )
                updated_data.append(event)

        return updated_data

    def get_sensors_addresses_on_trunk(self, trunk_number):
        return self._sensors_addresses_per_trunk[trunk_number]

    def get_sensors_per_trunk_count(self):
        return [self._sensors_per_trunk_count[trunk_number] for trunk_number in sorted(self._sensors_per_trunk_count.keys())]

    def hex_device_address_for_communicator(self):
        return "0x{0:02x}".format(self.controller_address)
