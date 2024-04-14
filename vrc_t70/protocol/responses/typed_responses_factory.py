import typing

from vrc_t70 import exceptions
from vrc_t70.protocol import requests, responses


class ResponsesFactory:
    """
    Factory used to create typed responses from decoded raw data represented in RawResponseData()
    """
    def __init__(self):
        self.data = {
            requests.RequestCodes.PING: responses.PingResponse,
            requests.RequestCodes.GET_SESSION_ID: responses.GetSessionIdResponse,
            requests.RequestCodes.SET_SESSION_ID: responses.SetSessionIdResponse,
            requests.RequestCodes.RESCAN_SENSORS_ON_TRUNK: responses.RescanSensorsOnTrunkResponse,
            requests.RequestCodes.GET_SENSORS_COUNT_ON_TRUNK: responses.GetSensorsCountOnTrunkResponse,
            requests.RequestCodes.GET_TEMPERATURE_OF_SENSOR_ON_TRUNK: responses.GetTemperatureOfSensorOnTrunkResponse,
            requests.RequestCodes.GET_SENSOR_UNIQUE_ADDRESS_ON_TRUNK: responses.GetSensorUniqueAddressOnTrunkResponse,
            requests.RequestCodes.GET_TEMPERATURES_ON_TRUNK: responses.GetTemperaturesOnTrunkResponse,
            requests.RequestCodes.GET_SENSORS_UNIQUE_ADDRESS_ON_TRUNK: responses.GetSensorsUniqueAddressOnTrunkResponse,
            requests.RequestCodes.SET_CONTROLLER_NEW_ADDRESS: responses.SetControllerNewAddressResponse,
        }

    def create(self, raw_response: responses.RawResponseData) -> responses.BaseResponse:
        """
        Creates typed response based on raw data in a form of RawResponseData() instance
        """
        if raw_response.event_id not in self.data:
            raise exceptions.ErrorUnknownResponse()

        klass = self.data[raw_response.event_id]
        klass = typing.cast(responses.BaseResponse, klass)
        return klass(raw_response)
