import pytest

from vrc_t70 import exceptions
from vrc_t70.protocol import requests


def test_can_serialize_request_without_payload():
    request = requests.BaseRequest(
        address=0xaa,
        request_id=0xbb,
        sequence_id=0xccdd,
    )

    data = request.serialize()
    assert data == bytes([0xaa, 0xbb, 0xcc, 0xdd, 0x00, 0x7b])


def test_can_serialize_request_with_payload():
    request = requests.BaseRequest(
        address=0xaa,
        request_id=0xbb,
        sequence_id=0xccdd,
        data=bytes([0x01, 0x02, 0x03, 0x04, 0x05])
    )

    data = request.serialize()
    assert data == bytes([0xaa, 0xbb, 0xcc, 0xdd, 0x05, 0x01, 0x02, 0x03, 0x04, 0x05, 0xae])


def test_can_serialize_request_without_payload_converting_to_bytes():
    request = requests.BaseRequest(
        address=0xaa,
        request_id=0xbb,
        sequence_id=0xccdd
    )

    expected_data = bytes([0xaa, 0xbb, 0xcc, 0xdd, 0x00, 0x7b])
    assert len(request) == len(expected_data)
    assert bytes(request) == expected_data


def test_can_serialize_request_with_payload_using_bytes():
    request = requests.BaseRequest(
        address=0xaa,
        request_id=0xbb,
        sequence_id=0xccdd,
        data=bytes([0x01, 0x02, 0x03, 0x04, 0x05])
    )

    expected_data = bytes([0xaa, 0xbb, 0xcc, 0xdd, 0x05, 0x01, 0x02, 0x03, 0x04, 0x05, 0xae])
    assert len(request) == len(expected_data)
    assert bytes(request) == expected_data


def test_throws_error_when_no_address_specified():
    request = requests.BaseRequest(
        request_id=0xbb,
        sequence_id=0xccdd,
        data=bytes([0x01, 0x02, 0x03, 0x04, 0x05])
    )
    with pytest.raises(exceptions.ErrorValueError):
        _ = bytes(request)


def test_throws_error_when_no_session_id_specified():
    request = requests.BaseRequest(
        address=0x08,
        request_id=0xbb,
        data=bytes([0x01, 0x02, 0x03, 0x04, 0x05])
    )
    with pytest.raises(exceptions.ErrorValueError):
        _ = bytes(request)
