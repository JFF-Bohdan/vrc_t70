import pytest

from tests.support import common_packets

from vrc_t70 import exceptions
from vrc_t70.protocol import requests, responses

TEST_DATA = {
    requests.RequestCodes.PING: common_packets.PING_RESPONSE,
    requests.RequestCodes.GET_SESSION_ID: common_packets.GET_SESSION_ID_RESPONSE,
    requests.RequestCodes.SET_SESSION_ID: common_packets.SET_SESSION_ID_RESPONSE,
    requests.RequestCodes.RESCAN_SENSORS_ON_TRUNK: common_packets.RESCAN_SENSORS_ON_TRUNK_RESPONSE,
    requests.RequestCodes.GET_SENSORS_COUNT_ON_TRUNK: common_packets.GET_SENSORS_COUNT_ON_TRUNK_RESPONSE,
    requests.RequestCodes.GET_TEMPERATURE_OF_SENSOR_ON_TRUNK:
        common_packets.GET_TEMPERATURE_OF_SENSOR_ON_TRUNK_RESPONSE,
    requests.RequestCodes.GET_SENSOR_UNIQUE_ADDRESS_ON_TRUNK:
        common_packets.GET_SENSOR_UNIQUE_ADDRESS_ON_TRUNK_RESPONSE,
    requests.RequestCodes.GET_TEMPERATURES_ON_TRUNK:
        common_packets.GET_TEMPERATURES_ON_TRUNK_RESPONSE_5_SENSORS,
    requests.RequestCodes.GET_SENSORS_UNIQUE_ADDRESS_ON_TRUNK:
        common_packets.GET_SENSORS_UNIQUE_ADDRESS_ON_TRUNK_RESPONSE_4_SENSORS,
    requests.RequestCodes.SET_CONTROLLER_NEW_ADDRESS:
        common_packets.SET_CONTROLLER_NEW_ADDRESS_RESPONSE,
}


def test_raises_exception_on_unknown_event_id():
    non_existing_raw_response = responses.deserialize(data=bytes([0x01, 0xff, 0x22, 0x33, 0x00, 0x00, 0x49]))
    factory = responses.ResponsesFactory()
    with pytest.raises(exceptions.ErrorUnknownResponse):
        factory.create(raw_response=non_existing_raw_response)


def test_can_create_all_classes():
    seen_classes = set()
    factory = responses.ResponsesFactory()

    for event_id, event_bytes in TEST_DATA.items():
        raw_response = responses.deserialize(data=event_bytes)
        typed_event = factory.create(raw_response=raw_response)
        assert typed_event is not None
        assert isinstance(typed_event, responses.BaseResponse)

        # Factory should create instances of different classes for different requests
        class_name = type(typed_event)
        assert class_name not in seen_classes
        seen_classes.add(class_name)


def test_have_test_cases_for_all_classes_supported_by_factory():
    factory = responses.ResponsesFactory()
    assert set(TEST_DATA.keys()) == set(factory.data.keys())


def test_have_test_cases_for_all_existing_request():
    assert set(TEST_DATA.keys()) == set(requests.RequestCodes.all_known_codes())
