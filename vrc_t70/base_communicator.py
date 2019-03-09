import time


from .limitations import MIN_DELAY_BETWEEN_REQUESTS
from .response import VrcT70Response


class BadCrc(Exception):
    pass


class WrongEventId(Exception):
    pass


class WrongControllerAddress(Exception):
    pass


class VrcT70CommunicatorBase(object):
    def __init__(self, serial, controller_address=0x01):
        self._serial = serial
        self.controller_address = controller_address
        self._last_request_time = None

    def send_command(self, cmd):
        self._make_delay_before_request()

        self._send_command(cmd)
        res = self._read_response(cmd.command)

        self._last_request_time = time.time()
        return res

    def _make_delay_before_request(self):
        if self._last_request_time is None:
            return

        delta = time.time() - self._last_request_time
        if delta >= MIN_DELAY_BETWEEN_REQUESTS:
            return

        time.sleep(MIN_DELAY_BETWEEN_REQUESTS - delta)

    def _send_command(self, cmd):
        sent_bytes = self._serial.write(bytes(cmd))

        if sent_bytes != len(cmd):
            raise Exception("Can't send request")

    def _read_response(self, expected_event_id):
        # 1 byte - device address
        # 1 byte - id event
        # 2 bytes - sequence id
        # 1 byte - processing result
        # 1 byte - data length
        # N bytes - data,
        # 1 bytes - crc 8
        expected_bytes_count = 7
        read_bytes = self._serial.read(expected_bytes_count)

        if len(read_bytes) != expected_bytes_count:
            raise Exception(
                "Can't read response. read_bytes_count = {} expected_bytes_count = {}".format(
                    len(read_bytes),
                    expected_bytes_count
                )
            )

        res = VrcT70Response()

        res.address = read_bytes[0]
        res.id_event = read_bytes[1]
        res.sequence_id = (read_bytes[2] << 8) | (read_bytes[3])
        res.processing_result = read_bytes[4]

        data_length = read_bytes[5]
        expected_crc = read_bytes[6]

        if data_length > 0:
            data = bytearray([expected_crc])

            buffer = self._serial.read(data_length)
            expected_crc = buffer[-1]

            data.extend(buffer[:-1])

            res.data = data

        res.crc = expected_crc

        if not res.is_crc_valid():
            raise BadCrc()

        if res.id_event != expected_event_id:
            raise WrongEventId()

        if res.address != self.controller_address:
            raise WrongControllerAddress()

        return res
