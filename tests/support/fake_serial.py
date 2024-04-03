import typing

from vrc_t70 import defaults


class FakeSerial:
    def __init__(
            self,
            responses: typing.Union[None, bytes, bytearray, list[bytes | bytearray | typing.Callable]] = None
    ):
        self.written_data = []

        self.responses = responses
        self.responses_offset = 0

        self.read_calls_qty = 0
        self.write_calls_qty = 0
        self.flush_call_qty = 0

        self.baudrate = defaults.DEFAULT_PORT_SPEED

    def write(self, data) -> int:
        self.write_calls_qty += 1
        self.written_data.append(data)
        return len(data)

    def read(self, size: int):
        self.read_calls_qty += 1
        if self.responses is None:
            return bytes()

        if isinstance(self.responses, list):
            try:
                response_item = self.responses[self.responses_offset]
                if callable(response_item):
                    return response_item(size)

                return bytes(response_item)
            finally:
                self.responses_offset += 1

        if isinstance(self.responses, (bytes, bytearray)):
            result = bytes(self.responses[self.responses_offset: self.responses_offset + size])
            assert isinstance(result, bytes)
            self.responses_offset += len(result)
            return bytes(result)

        raise ValueError("Unknown response type, don't know how to use it")

    def flush(self):
        self.flush_call_qty += 1

    def flushOutput(self):
        pass

    def flushInput(self):
        pass
