import itertools
import typing

import pytest

from tests.support import common_packets
from tests.support import ex_time_machine
from tests.support import fake_serial

from vrc_t70 import exceptions
from vrc_t70.communicator import base_communicator
from vrc_t70.protocol.requests import get_session_id_request
from vrc_t70.protocol.responses.typed import get_session_id_response


def wrong_and_right_sequence_id() -> bytes:
    wrong_response = bytes([0x01, 0x07, 0x10, 0x20, 0x00, 0x04, 0xca, 0xfe, 0xba, 0xbe, 0x32])
    combined_data = bytes([item for item in itertools.chain(wrong_response, common_packets.GET_SESSION_ID_RESPONSE)])

    assert combined_data == bytes(
        [
            0x01, 0x07, 0x10, 0x20, 0x00, 0x04, 0xca, 0xfe, 0xba, 0xbe, 0x32,
            0x08, 0x07, 0x22, 0x33, 0x00, 0x04, 0xde, 0xad, 0xbe, 0xef, 0x0b,
        ]
    )
    return combined_data


@ex_time_machine.travel(123000, tick_delta=0.02)
def test_ignores_response_from_controller_with_wrong_address_and_gets_correct_one():
    # Response controller with wrong address
    combined_data = wrong_and_right_sequence_id()

    fake_port = fake_serial.FakeSerial(responses=combined_data)
    communicator = base_communicator.BaseVrcT70Communicator(
        port=fake_port,
        address=0x08,
        sequence_id=0x2233,
    )
    response = communicator.communicate(get_session_id_request.GetSessionIdRequest())
    response = typing.cast(get_session_id_response.GetSessionIdResponse, response)
    assert response.session_id == 0xdeadbeef
    assert fake_port.written_data == [common_packets.GET_SESSION_ID_REQUEST] * 2


def test_raises_exception_on_response_from_controller_with_wrong_address():
    # Response controller with wrong address
    combined_data = wrong_and_right_sequence_id()

    fake_port = fake_serial.FakeSerial(responses=combined_data)
    communicator = base_communicator.BaseVrcT70Communicator(
        port=fake_port,
        address=0x08,
        sequence_id=0x2233,
    )
    communicator.raise_exception_on_response_with_wrong_address = True
    with pytest.raises(exceptions.ErrorResponseFromControllerWithWrongAddress) as e:
        _ = communicator.communicate(get_session_id_request.GetSessionIdRequest())
        assert e.unexpected_address == 1
        assert e.expected_address == 8


@ex_time_machine.travel(123000)
def test_raises_exception_when_no_response_from_expected_controller():
    fake_port = fake_serial.FakeSerial(
        responses=bytes([0x01, 0x07, 0x10, 0x20, 0x00, 0x04, 0xca, 0xfe, 0xba, 0xbe, 0x32])
    )
    communicator = base_communicator.BaseVrcT70Communicator(
        port=fake_port,
        address=0x08,
        sequence_id=0x2233,
    )
    with pytest.raises(exceptions.ErrorNoResponseFromController):
        _ = communicator.communicate(get_session_id_request.GetSessionIdRequest())
