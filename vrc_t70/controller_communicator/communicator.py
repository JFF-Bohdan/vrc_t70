import logging
import typing

import serial

from vrc_t70 import controller_communicator, defaults, exceptions, limitations
from vrc_t70.protocol import requests, responses

logger = logging.getLogger(__name__)


class VrcT70Communicator(controller_communicator.BaseVrcT70Communicator):
    def __init__(
            self,
            port: typing.Optional[serial.Serial] = None,
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
        self._communicate_and_validate_response_type(requests.PingRequest(), responses.PingResponse)

    def get_session_id(self) -> int:
        """
        Sets session id
        """
        logger.debug("Querying session id")
        response = self._communicate_and_validate_response_type(
            requests.GetSessionIdRequest(),
            responses.GetSessionIdResponse
        )

        response = typing.cast(responses.GetSessionIdResponse, response)
        return response.session_id

    def set_session_id(self, session_id: int) -> int:
        """
        Used to set session id which is used to communicate with controller. Returns new session id
        """
        logger.debug("Setting session id")

        if (session_id <= 0) or (session_id > limitations.MAX_SESSION_ID):
            raise exceptions.ErrorValueError(f"Session id must be more than 0 and less {limitations.MAX_SESSION_ID}")

        response = self._communicate_and_validate_response_type(
            requests.SetSessionIdRequest(
                session_id=session_id
            ),
            responses.SetSessionIdResponse
        )

        response = typing.cast(responses.SetSessionIdResponse, response)
        self._validate_expected_session_id(expected=session_id, received=response.session_id)
        return response.session_id

    def rescan_sensors_on_trunk(self, trunk_number: int) -> int:
        """
        Rescans sensors on trunk
        """
        limitations.validate_trunk_number(trunk_number)

        logger.debug(f"Rescanning sensors on trunk {trunk_number}")
        response = self._communicate_and_validate_response_type(
            requests.RescanSensorsOnTrunkRequest(trunk_number=trunk_number),
            responses.RescanSensorsOnTrunkResponse
        )

        response = typing.cast(responses.RescanSensorsOnTrunkResponse, response)
        self._validate_expected_trunk_number(expected=trunk_number, received=response.trunk_number)
        return response.sensors_count

    def get_get_sensors_count_on_trunk(self, trunk_number: int) -> int:
        """
        Requests sensors count on trunk
        """

        limitations.validate_trunk_number(trunk_number)

        logger.debug(f"Retrieving sensors count on trunk {trunk_number}")
        response = self._communicate_and_validate_response_type(
            requests.GetSensorsCountOnTrunkRequest(trunk_number=trunk_number),
            responses.GetSensorsCountOnTrunkResponse
        )

        response = typing.cast(responses.GetSensorsCountOnTrunkResponse, response)

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
            requests.GetTemperatureOfSensorOnTrunkRequest(
                trunk_number=trunk_number,
                sensor_index=sensor_index
            ),
            responses.GetTemperatureOfSensorOnTrunkResponse
        )

        response = typing.cast(
            responses.GetTemperatureOfSensorOnTrunkResponse,
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
    ) -> list[responses.data_types.SensorTemperatureInfo]:
        limitations.validate_trunk_number(trunk_number)

        logger.debug(f"Requesting temperature of sensors on trunk {trunk_number}")
        response = self._communicate_and_validate_response_type(
            requests.GetTemperaturesOnTrunkRequest(
                trunk_number=trunk_number
            ),
            responses.GetTemperaturesOnTrunkResponse
        )

        response = typing.cast(
            responses.GetTemperaturesOnTrunkResponse,
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
            requests.GetSensorUniqueAddressOnTrunkRequest(
                trunk_number=trunk_number,
                sensor_index=sensor_index
            ),
            responses.GetSensorUniqueAddressOnTrunkResponse
        )

        response = typing.cast(
            responses.GetSensorUniqueAddressOnTrunkResponse,
            response
        )

        self._validate_expected_trunk_number(expected=trunk_number, received=response.trunk_number)
        self._validate_expected_sensor_index(expected=sensor_index, received=response.sensor_index)

        return response.sensor_address

    def get_sensors_unique_address_on_trunk(self, trunk_number: int) -> list[responses.data_types.SensorAddressInfo]:
        limitations.validate_trunk_number(trunk_number)

        logger.debug(f"Requesting addresses of sensor on trunk {trunk_number}")
        response = self._communicate_and_validate_response_type(
            requests.GetSensorsUniqueAddressOnTrunkRequest(
                trunk_number=trunk_number,
            ),
            responses.GetSensorsUniqueAddressOnTrunkResponse
        )

        response = typing.cast(
            responses.GetSensorsUniqueAddressOnTrunkResponse,
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
            requests.SetControllerNewAddressRequest(
                new_controller_address=new_controller_address
            ),
            responses.SetControllerNewAddressResponse
        )

        response = typing.cast(responses.SetControllerNewAddressResponse, response)
        if response.new_address != new_controller_address:
            raise exceptions.ErrorUnknownResponse(
                f"Received unexpected controller address in response. Expected: {new_controller_address}. "
                f"Received {response.new_address}."
            )

        self.address = new_controller_address

    def _communicate_and_validate_response_type(
            self,
            request: requests.BaseRequest,
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
