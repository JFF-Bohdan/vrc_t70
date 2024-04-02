import typing
from unittest import mock

import pytest

from tests.support import common_packets
from tests.support import fake_serial

from vrc_t70 import exceptions
from vrc_t70.communicator import base_communicator
from vrc_t70.protocol.requests import get_session_id_request, ping_request
from vrc_t70.protocol.responses.typed import get_session_id_response, ping_response


def test_can_create_communicator():
    port = fake_serial.FakeSerial()
    _ = base_communicator.BaseVrcT70Communicator(
        port=port
    )
    assert port.written_data == []


def test_can_perform_ping_and_get_pong_response():
    fake_port = fake_serial.FakeSerial(
        responses=[common_packets.PING_RESPONSE]
    )
    communicator = base_communicator.BaseVrcT70Communicator(
        port=fake_port,
        address=0x08,
        sequence_id=0x2233
    )
    response = communicator._communicate(ping_request.PingRequest())
    assert isinstance(response, ping_response.PingResponse)
    assert fake_port.written_data == [common_packets.PING_REQUEST]


def test_will_use_address_from_request_when_specified():
    fake_port = fake_serial.FakeSerial(
        responses=[common_packets.PING_RESPONSE]
    )
    communicator = base_communicator.BaseVrcT70Communicator(
        port=fake_port,
        address=0x05,
        sequence_id=0x0102
    )
    response = communicator._communicate(ping_request.PingRequest(address=0x08, sequence_id=0x2233))
    assert isinstance(response, ping_response.PingResponse)
    assert fake_port.written_data == [common_packets.PING_REQUEST]


def test_will_use_address_from_communicator_when_no_address_in_request():
    fake_port = fake_serial.FakeSerial(
        responses=[common_packets.PING_RESPONSE]
    )
    communicator = base_communicator.BaseVrcT70Communicator(
        port=fake_port,
        address=0x08,
        sequence_id=0x2233
    )
    response = communicator._communicate(ping_request.PingRequest())
    assert isinstance(response, ping_response.PingResponse)
    assert fake_port.written_data == [common_packets.PING_REQUEST]


def test_retries_when_no_responses_and_then_gives_up():
    fake_port = fake_serial.FakeSerial()
    communicator = base_communicator.BaseVrcT70Communicator(
        port=fake_port,
        address=0x42,
        requests_retries_count=5
    )
    with pytest.raises(exceptions.ErrorNoResponseFromController):
        communicator._communicate(ping_request.PingRequest(address=0x08, sequence_id=0x2233))

    assert fake_port.written_data == [common_packets.PING_REQUEST] * 5


def test_can_ping_when_port_sends_only_one_symbol_at_time():
    sent_data = bytes()

    def single_byte_write(data) -> int:
        nonlocal sent_data
        sent_data += bytes([data[0]])
        return 1

    fake_port = fake_serial.FakeSerial(
        responses=[common_packets.PING_RESPONSE]
    )
    fake_port.write = mock.Mock(side_effect=single_byte_write)

    communicator = base_communicator.BaseVrcT70Communicator(
        port=fake_port,
        address=0x08,
        sequence_id=0x2233,
    )
    request = ping_request.PingRequest(address=0x08, sequence_id=0x2233)
    expected_sent_bytes = bytes(request)

    response = communicator._communicate(request)
    assert isinstance(response, ping_response.PingResponse)
    assert sent_data == expected_sent_bytes


def test_can_ping_when_controller_is_slow():
    slow_response = [bytes([item]) for item in common_packets.PING_RESPONSE]
    assert slow_response == [
        bytes([0x08]),
        bytes([0x01]),
        bytes([0x22]),
        bytes([0x33]),
        bytes([0x00]),
        bytes([0x00]),
        bytes([0xf0])
    ]
    fake_port = fake_serial.FakeSerial(responses=slow_response)
    communicator = base_communicator.BaseVrcT70Communicator(
        port=fake_port,
        address=0x08,
        sequence_id=0x2233,
    )
    communicator._communicate(ping_request.PingRequest())
    assert fake_port.written_data == [common_packets.PING_REQUEST]


def test_can_communicate_with_slow_controller_when_response_contains_payload():
    slow_response = [bytes([item]) for item in common_packets.GET_SESSION_ID_RESPONSE]
    fake_port = fake_serial.FakeSerial(responses=slow_response)
    communicator = base_communicator.BaseVrcT70Communicator(
        port=fake_port,
        address=0x08,
        sequence_id=0x2233,
    )
    response = communicator._communicate(get_session_id_request.GetSessionIdRequest())
    response = typing.cast(get_session_id_response.GetSessionIdResponse, response)
    assert response.session_id == 0xdeadbeef
    assert fake_port.written_data == [common_packets.GET_SESSION_ID_REQUEST]


def test_adjusts_sequence_id_on_overflow():
    responses = [
        bytes([0x08, 0x01, 0xff, 0xfd, 0x00, 0x00, 0xfb]),
        bytes([0x08, 0x01, 0xff, 0xfe, 0x00, 0x00, 0xab]),
        bytes([0x08, 0x01, 0xff, 0xff, 0x00, 0x00, 0x28]),
        bytes([0x08, 0x01, 0x00, 0x00, 0x00, 0x00, 0x88]),
    ]

    fake_port = fake_serial.FakeSerial(responses=responses)
    communicator = base_communicator.BaseVrcT70Communicator(
        port=fake_port,
        address=0x08,
        sequence_id=0xfffd,
    )
    communicator._communicate(ping_request.PingRequest())
    communicator._communicate(ping_request.PingRequest())
    communicator._communicate(ping_request.PingRequest())
    communicator._communicate(ping_request.PingRequest())
