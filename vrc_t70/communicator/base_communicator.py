import binascii
import copy
import logging
import time
import typing

import serial

from vrc_t70 import defaults
from vrc_t70 import exceptions
from vrc_t70 import limitations
from vrc_t70 import shared
from vrc_t70.protocol.requests import base_request
from vrc_t70.protocol.responses import base_response, raw_response_data, typed_responses_factory


logger = logging.getLogger("vrct70.base_communicator")


class BaseVrcT70Communicator:
    def __init__(
        self,
        port: serial.Serial,
        address: int = defaults.DEFAULT_CONTROLLER_ADDRESS,
        requests_retries_count: int = defaults.DEFAULT_MAX_RETRIES_FOR_REQUEST,
        min_delay_between_requests: int = defaults.MIN_DELAY_BETWEEN_REQUESTS,
        sequence_id: int = 1,
    ):
        self.port = port

        self.address = address
        limitations.validate_controller_address(self.address)

        if sequence_id:
            limitations.validate_sequence_id(sequence_id)
        self.sequence_id = sequence_id

        self.requests_retries_count = requests_retries_count
        self.min_delay_between_requests = min_delay_between_requests

        self._last_request_time = None

        self._responses_factory = typed_responses_factory.ResponsesFactory()

        self._max_symbol_wait_time = shared.default_wait_time_for_symbol(self.port.baudrate)

        self.raise_exception_on_response_with_wrong_address = False
        self.min_wait_time_for_response = 0.075

        self.validate_sequence_id = True

    def communicate(self, request: base_request.BaseRequest) -> base_response.BaseResponse:
        """
        Sends request to a controller and then receives response and creates typed
        class which represents response
        """
        for attempt in range(1, self.requests_retries_count + 1):
            self._make_delay_before_request()

            try:
                request = self._prepare_request(request)
                self._send_request(request, attempt=attempt)
                raw_response = self._read_response(
                    additional_wait_time_for_response=request.additional_wait_time_for_response
                )
                logger.debug(f"Decoded response: {raw_response}")

                if raw_response.address != request.address:
                    msg = f"Received response from wrong controller with address {raw_response.address}, " \
                          f"expected address {request.address}"
                    logger.warning(msg)

                    if self.raise_exception_on_response_with_wrong_address:
                        raise exceptions.ErrorResponseFromControllerWithWrongAddress(
                            msg,
                            unexpected_address=raw_response.address,
                            expected_address=request.address
                        )

                    continue

                if self.validate_sequence_id and (raw_response.sequence_id != request.sequence_id):
                    logger.warning(
                        f"Received response with wrong sequence id. "
                        f"Received {raw_response.sequence_id}, expected {request.sequence_id}"
                    )
                    continue

                return self._responses_factory.create(raw_response=raw_response)
            except exceptions.ErrorResponseFromControllerWithWrongAddress:
                raise
            except exceptions.ErrorBaseVrcT70 as e:
                logger.debug(f"Can't communicate with controller (type={type(e)}): {e}")
                self.port.flushInput()
                continue

        raise exceptions.ErrorNoResponseFromController("No response from controller")

    def _send_request(self, request: base_request.BaseRequest, attempt: int):
        """
        Sends prepared request, where should have all values assigned
        """
        data = bytes(request)

        debug_data = binascii.hexlify(data).decode("ascii")
        logger.debug(f"Sending (attempt {attempt}): {debug_data}")

        self._write(data)

        self._last_request_time = time.monotonic()
        self.sequence_id += 1
        if self.sequence_id > limitations.MAX_SEQUENCE_ID:
            self.sequence_id = limitations.MIN_SEQUENCE_ID

    def _read_response(
            self,
            additional_wait_time_for_response: typing.Optional[float] = None
    ) -> raw_response_data.RawResponseData:
        # 1 byte - device address
        # 1 byte - id event
        # 2 bytes - sequence id
        # 1 byte - processing result
        # 1 byte - data length
        # N bytes - data,
        # 1 bytes - crc 8
        expected_bytes_count = 7
        additional_wait_time_for_response = 0.0 if additional_wait_time_for_response < 0.0 \
            else additional_wait_time_for_response
        if additional_wait_time_for_response < self.min_wait_time_for_response:
            additional_wait_time_for_response = self.min_wait_time_for_response

        raw_bytes, spent_time = self._read(expected_bytes_count, additional_wait_time_for_response)
        additional_wait_time_for_response -= spent_time
        additional_wait_time_for_response = 0.0 if additional_wait_time_for_response < 0.0 \
            else additional_wait_time_for_response

        # Attempting to read packet with length 7, which would be a packet without any data
        # In case we would have a response with payload, we would read additional necessary data in a moment
        if len(raw_bytes) != expected_bytes_count:
            raise exceptions.ErrorReadingResponse(
                f"Can't read response. received bytes count {len(raw_bytes)} "
                f"expected bytes count {expected_bytes_count}"
            )

        payload_length = raw_bytes[5]
        if payload_length:
            payload, _ = self._read(payload_length, additional_wait_time_for_response)
            raw_bytes = raw_bytes + payload

        debug_data = binascii.hexlify(raw_bytes).decode("ascii")
        logger.debug(f"Received: {debug_data}")

        return raw_response_data.deserialize(bytes(raw_bytes))

    def _make_delay_before_request(self):
        if self._last_request_time is None:
            return

        delta = time.monotonic() - self._last_request_time
        if delta >= self.min_delay_between_requests:
            return

        time.sleep(self.min_delay_between_requests - delta)

    def _write(self, data: bytes) -> int:
        """
        Sends given bytes. In case if needed, repeats calls to port.write if port can't send all bytes at once
        """

        sent_bytes = 0
        total_length = len(data)
        while sent_bytes < total_length:
            sent_bytes += self.port.write(data[sent_bytes: total_length])

        self.port.flushOutput()
        return sent_bytes

    def _read(self, bytes_needed: int, additional_wait_time_for_response: float) -> tuple[bytes, float]:
        max_wait_time = bytes_needed * self._max_symbol_wait_time + additional_wait_time_for_response
        logger.debug(f"Max wait time for reading is: {round(max_wait_time, 3)}")
        result = bytes()

        timestamp_begin = time.monotonic()
        while (len(result) != bytes_needed) and ((time.monotonic() - timestamp_begin) <= max_wait_time):
            result += self.port.read(bytes_needed - len(result))

        time_spent = time.monotonic() - timestamp_begin
        return result, time_spent

    def _prepare_request(self, request: base_request.BaseRequest) -> base_request.BaseRequest:
        request = copy.deepcopy(request)
        if request.address is None:
            request.address = self.address

        if request.sequence_id is None:
            request.sequence_id = self.sequence_id

        return request
