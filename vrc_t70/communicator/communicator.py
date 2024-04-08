import logging
import typing

import serial

from vrc_t70 import defaults
from vrc_t70 import exceptions
from vrc_t70 import limitations
from vrc_t70.communicator import base_communicator
from vrc_t70.protocol.requests import base_request, get_sensor_unique_address_on_trunk_request, \
    get_sensors_count_on_trunk_request, get_sensors_unique_address_on_trunk_request, get_session_id_request, \
    get_temperature_of_sensor_on_trunk_request, get_temperatures_on_trunk_request, ping_request, \
    rescan_sensors_on_trunk_request, set_controller_new_address_request, set_session_id_request
from vrc_t70.protocol.responses.typed import data_types, get_sensor_unique_address_on_trunk_response, \
    get_sensors_count_on_trunk_response, get_sensors_unique_address_on_trunk_response, get_session_id_response, \
    get_temperature_of_sensor_on_trunk_response, get_temperatures_on_trunk_response, ping_response, \
    rescan_sensors_on_trunk_response, set_controller_new_address_response, set_session_id_response


logger = logging.getLogger("vrct70.communicator")


class VrcT70Communicator(base_communicator.BaseVrcT70Communicator):
    def __init__(
            self,
            port: serial.Serial,
            address: int = defaults.DEFAULT_CONTROLLER_ADDRESS,
            requests_retries_count: int = defaults.DEFAULT_MAX_RETRIES_FOR_REQUEST,
            sequence_id: int = 1
    ):
        super().__init__(
            port=port,
            address=address,
            requests_retries_count=requests_retries_count,
            sequence_id=sequence_id
        )

    def ping(self) -> None:
        """
        Sends ping request to check that controller is available
        """
        logger.debug("Sending PING request")
        self._communicate_and_validate_response_type(ping_request.PingRequest(), ping_response.PingResponse)

    def get_session_id(self) -> int:
        """
        Sets session id
        """
        logger.debug("Querying session id")
        response = self._communicate_and_validate_response_type(
            get_session_id_request.GetSessionIdRequest(),
            get_session_id_response.GetSessionIdResponse
        )

        response = typing.cast(get_session_id_response.GetSessionIdResponse, response)
        return response.session_id

    def set_session_id(self, session_id: int) -> int:
        """
        Used to set session id which is used to communicate with controller. Returns new session id
        """
        logger.debug("Setting session id")

        if (session_id <= 0) or (session_id > limitations.MAX_SESSION_ID):
            raise exceptions.ErrorValueError(f"Session id must be more than 0 and less {limitations.MAX_SESSION_ID}")

        response = self._communicate_and_validate_response_type(
            set_session_id_request.SetSessionIdRequest(
                session_id=session_id
            ),
            set_session_id_response.SetSessionIdResponse
        )

        response = typing.cast(set_session_id_response.SetSessionIdResponse, response)
        self._validate_expected_session_id(expected=session_id, received=response.session_id)
        return response.session_id

    def rescan_sensors_on_trunk(self, trunk_number: int) -> int:
        """
        Rescans sensors on trunk
        """
        limitations.validate_trunk_number(trunk_number)

        logger.debug(f"Rescanning sensors on trunk {trunk_number}")
        response = self._communicate_and_validate_response_type(
            rescan_sensors_on_trunk_request.RescanSensorsOnTrunkRequest(trunk_number=trunk_number),
            rescan_sensors_on_trunk_response.RescanSensorsOnTrunkResponse
        )

        response = typing.cast(rescan_sensors_on_trunk_response.RescanSensorsOnTrunkResponse, response)
        self._validate_expected_trunk_number(expected=trunk_number, received=response.trunk_number)
        return response.sensors_count

    def get_get_sensors_count_on_trunk(self, trunk_number: int) -> int:
        """
        Requests sensors count on trunk
        """

        limitations.validate_trunk_number(trunk_number)

        logger.debug(f"Retrieving sensors count on trunk {trunk_number}")
        response = self._communicate_and_validate_response_type(
            get_sensors_count_on_trunk_request.GetSensorsCountOnTrunkRequest(trunk_number=trunk_number),
            get_sensors_count_on_trunk_response.GetSensorsCountOnTrunkResponse
        )

        response = typing.cast(get_sensors_count_on_trunk_response.GetSensorsCountOnTrunkResponse, response)

        self._validate_expected_trunk_number(expected=trunk_number, received=response.trunk_number)
        return response.sensors_count

    def get_temperature_of_sensor_on_trunk(self, trunk_number: int, sensor_index: int) -> typing.Optional[float]:
        """
        Requests temperature of specific sensor on a trunk
        """

        limitations.validate_trunk_number(trunk_number)
        limitations.validate_sensor_index(sensor_index)

        logger.debug(f"Requesting temperature of sensor (index={sensor_index}) on trunk {trunk_number}")
        response = self._communicate_and_validate_response_type(
            get_temperature_of_sensor_on_trunk_request.GetTemperatureOfSensorOnTrunkRequest(
                trunk_number=trunk_number,
                sensor_index=sensor_index
            ),
            get_temperature_of_sensor_on_trunk_response.GetTemperatureOfSensorOnTrunkResponse
        )

        response = typing.cast(
            get_temperature_of_sensor_on_trunk_response.GetTemperatureOfSensorOnTrunkResponse,
            response
        )

        self._validate_expected_trunk_number(
            expected=trunk_number,
            received=response.sensor_temperature.trunk_number
        )
        self._validate_expected_sensor_index(
            expected=sensor_index,
            received=response.sensor_temperature.sensor_index
        )
        return response.sensor_temperature.temperature

    def get_temperature_of_sensors_on_trunk(
            self,
            trunk_number: int
    ) -> list[data_types.SensorTemperatureInfo]:
        limitations.validate_trunk_number(trunk_number)

        logger.debug(f"Requesting temperature of sensors on trunk {trunk_number}")
        response = self._communicate_and_validate_response_type(
            get_temperatures_on_trunk_request.GetTemperaturesOnTrunkRequest(
                trunk_number=trunk_number
            ),
            get_temperatures_on_trunk_response.GetTemperaturesOnTrunkResponse
        )

        response = typing.cast(
            get_temperatures_on_trunk_response.GetTemperaturesOnTrunkResponse,
            response
        )

        for sensor in response.sensors_temperature:
            self._validate_expected_trunk_number(expected=trunk_number, received=sensor.trunk_number)
            limitations.validate_sensor_index(sensor_index=sensor.sensor_index)

        return response.sensors_temperature

    def get_sensor_unique_address_on_trunk(self, trunk_number: int, sensor_index: int) -> int:
        limitations.validate_trunk_number(trunk_number)
        limitations.validate_sensor_index(sensor_index)

        logger.debug(f"Requesting address of sensor (index={sensor_index}) on trunk {trunk_number}")
        response = self._communicate_and_validate_response_type(
            get_sensor_unique_address_on_trunk_request.GetSensorUniqueAddressOnTrunkRequest(
                trunk_number=trunk_number,
                sensor_index=sensor_index
            ),
            get_sensor_unique_address_on_trunk_response.GetSensorUniqueAddressOnTrunkResponse
        )

        response = typing.cast(
            get_sensor_unique_address_on_trunk_response.GetSensorUniqueAddressOnTrunkResponse,
            response
        )

        self._validate_expected_trunk_number(expected=trunk_number, received=response.trunk_number)
        self._validate_expected_sensor_index(expected=sensor_index, received=response.sensor_index)

        return response.sensor_address

    def get_sensors_unique_address_on_trunk(self, trunk_number: int) -> list[data_types.SensorAddressInfo]:
        limitations.validate_trunk_number(trunk_number)

        logger.debug(f"Requesting addresses of sensor on trunk {trunk_number}")
        response = self._communicate_and_validate_response_type(
            get_sensors_unique_address_on_trunk_request.GetSensorsUniqueAddressOnTrunkRequest(
                trunk_number=trunk_number,
            ),
            get_sensors_unique_address_on_trunk_response.GetSensorsUniqueAddressOnTrunkResponse
        )

        response = typing.cast(
            get_sensors_unique_address_on_trunk_response.GetSensorsUniqueAddressOnTrunkResponse,
            response
        )
        for item in response.sensors_address:
            self._validate_expected_trunk_number(expected=trunk_number, received=item.trunk_number)
            limitations.validate_sensor_index(item.sensor_index)

        return response.sensors_address

    def set_controller_new_address(self, new_controller_address: int) -> None:
        """
        Configures new address for controller. Automatically will adjust address
        used for communication to a new value
        """
        limitations.validate_controller_address(new_controller_address)
        logger.debug(f"Configuring new controller address {new_controller_address}")

        response = self._communicate_and_validate_response_type(
            set_controller_new_address_request.SetControllerNewAddressRequest(
                new_controller_address=new_controller_address
            ),
            set_controller_new_address_response.SetControllerNewAddressResponse
        )

        response = typing.cast(set_controller_new_address_response.SetControllerNewAddressResponse, response)
        if response.new_address != new_controller_address:
            raise exceptions.ErrorUnknownResponse(
                f"Received unexpected controller address in response. Expected: {new_controller_address}. "
                f"Received {response.new_address}."
            )

        self.address = new_controller_address

    def _communicate_and_validate_response_type(
            self,
            request: base_request.BaseRequest,
            expected_response_class: typing.Any
    ) -> typing.Any:
        """
        Sends given request, retrieves response and then validates that response class is expected one
        """
        response = super().communicate(request)
        logger.debug(f"Response type: {type(response)}")

        if not isinstance(response, expected_response_class):
            raise exceptions.ErrorUnknownResponse(
                f"Received response with wrong type. "
                f"Expected {expected_response_class} received {type(response)}"
            )

        return response

    @staticmethod
    def _validate_expected_session_id(expected: int, received: int) -> None:
        if expected != received:
            raise exceptions.ErrorUnknownResponse(
                f"Controller returned response with wrong session id. Expected {expected} received {received}"
            )

    @staticmethod
    def _validate_expected_trunk_number(expected: int, received: int) -> None:
        if expected != received:
            raise exceptions.ErrorUnknownResponse(
                f"Controller returned response for wrong trunk number. "
                f"Expected {expected} received {received}"
            )

    @staticmethod
    def _validate_expected_sensor_index(expected: int, received: int) -> None:
        if expected != received:
            raise exceptions.ErrorUnknownResponse(
                f"Controller returned response with wrong sensor index. Expected {expected} received {received}"
            )
