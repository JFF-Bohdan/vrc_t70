import typing

from vrc_t70 import exceptions
from vrc_t70.protocol.requests import request_codes
from vrc_t70.protocol.responses import base_response
from vrc_t70.protocol.responses import raw_response_data
from vrc_t70.protocol.responses.typed import get_sensor_unique_address_on_trunk_response, \
    get_sensors_count_on_trunk_response, get_sensors_unique_address_on_trunk_response, \
    get_session_id_response, get_temperature_of_sensor_on_trunk_response, get_temperatures_on_trunk_response, \
    ping_response, rescan_sensors_on_trunk_response, set_controller_new_address_response, set_session_id_response


class ResponsesFactory:
    """
    Factory used to create typed responses from decoded raw data represented in RawResponseData()
    """
    def __init__(self):
        self.data = {
            request_codes.RequestCodes.PING: ping_response.PingResponse,
            request_codes.RequestCodes.GET_SESSION_ID: get_session_id_response.GetSessionIdResponse,
            request_codes.RequestCodes.SET_SESSION_ID: set_session_id_response.SetSessionIdResponse,
            request_codes.RequestCodes.RESCAN_SENSORS_ON_TRUNK:
                rescan_sensors_on_trunk_response.RescanSensorsOnTrunkResponse,
            request_codes.RequestCodes.GET_SENSORS_COUNT_ON_TRUNK:
                get_sensors_count_on_trunk_response.GetSensorsCountOnTrunkResponse,
            request_codes.RequestCodes.GET_TEMPERATURE_OF_SENSOR_ON_TRUNK:
                get_temperature_of_sensor_on_trunk_response.GetTemperatureOfSensorOnTrunkResponse,
            request_codes.RequestCodes.GET_SENSOR_UNIQUE_ADDRESS_ON_TRUNK:
                get_sensor_unique_address_on_trunk_response.GetSensorUniqueAddressOnTrunkResponse,
            request_codes.RequestCodes.GET_TEMPERATURES_ON_TRUNK:
                get_temperatures_on_trunk_response.GetTemperaturesOnTrunkResponse,
            request_codes.RequestCodes.GET_SENSORS_UNIQUE_ADDRESS_ON_TRUNK:
                get_sensors_unique_address_on_trunk_response.GetSensorsUniqueAddressOnTrunkResponse,
            request_codes.RequestCodes.SET_CONTROLLER_NEW_ADDRESS:
                set_controller_new_address_response.SetControllerNewAddressResponse,
        }

    def create(self, raw_response: raw_response_data.RawResponseData) -> base_response.BaseResponse:
        """
        Creates typed response based on raw data in a form of RawResponseData() instance
        """
        if raw_response.event_id not in self.data:
            raise exceptions.ErrorUnknownResponse()

        klass = self.data[raw_response.event_id]
        klass = typing.cast(base_response.BaseResponse, klass)
        return klass(raw_response)
