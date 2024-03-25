import pytest

from tests.support import common_packets

from vrc_t70 import exceptions
from vrc_t70.protocol.responses import raw_response_data


def test_throws_error_on_empty_response():
    with pytest.raises(exceptions.ErrorEmptyResponse):
        raw_response_data.deserialize(data=bytes())


def test_throws_exception_on_wrong_crc():
    with pytest.raises(exceptions.ErrorWrongCrc):
        raw_response_data.deserialize(data=bytes([0x01, 0x01, 0x22, 0x33, 0x00, 0x00, 0xaa]))


def test_do_not_throws_exception_when_crc_is_valid():
    raw_data = raw_response_data.deserialize(data=bytes([0x01, 0x01, 0x22, 0x33, 0x00, 0x00, 0x56]))
    assert isinstance(raw_data, raw_response_data.RawResponseData)


def test_can_deserialize_response_with_payload():
    raw_data = bytes([0x01, 0x01, 0x22, 0x33, 0x00, 0x05, 0x01, 0x02, 0x03, 0x04, 0x05, 0x37])
    response = raw_response_data.deserialize(raw_data)
    expected_response = raw_response_data.RawResponseData(
        address=0x01,
        event_id=0x01,
        sequence_id=0x2233,
        processing_result=0x00,
        data_length=0x05,
        crc=0x37,
        payload=bytes([0x01, 0x02, 0x03, 0x04, 0x05])
    )

    assert response == expected_response


def test_throws_error_on_wrong_payload_length_less_then_expected():
    with pytest.raises(exceptions.ErrorWrongPayloadLength):
        raw_data = bytes([0x01, 0x01, 0x22, 0x33, 0x00, 0x10, 0x01, 0x02, 0x03, 0x04, 0x05, 0xcc])
        raw_response_data.deserialize(raw_data)


def test_throws_error_on_wrong_payload_length_more_then_expected():
    with pytest.raises(exceptions.ErrorWrongPayloadLength):
        raw_data = bytes([0x01, 0x01, 0x22, 0x33, 0x00, 0x05, 0x01, 0x02, 0x03, 0x04, 0x05, 0x06, 0x23])
        raw_response_data.deserialize(raw_data)


def test_can_deserialize_pong_response():
    raw_data = bytes(common_packets.PING_RESPONSE)
    response = raw_response_data.deserialize(raw_data)
    expected_response = raw_response_data.RawResponseData(
        address=0x08,
        event_id=0x01,
        sequence_id=0x2233,
        processing_result=0x00,
        data_length=0x00,
        crc=0xf0
    )

    assert response == expected_response


def test_can_deserialize_error_code_for_requests_processing():
    raw_data = common_packets.PING_RESPONSE_WITH_ERROR_CODE
    response = raw_response_data.deserialize(raw_data)
    expected_response = raw_response_data.RawResponseData(
        address=0x08,
        event_id=0x01,
        sequence_id=0x2233,
        processing_result=0xdd,
        data_length=0x00,
        crc=0x2b
    )

    assert response == expected_response
