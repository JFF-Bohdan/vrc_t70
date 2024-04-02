import typing

from vrc_t70 import crc
from vrc_t70 import exceptions


class BaseRequest:
    """
    Base class used to represent requests to VRC-T70
    """
    def __init__(
            self,
            request_id: int,
            address: typing.Optional[int] = None,
            sequence_id: typing.Optional[int] = None,
            data: typing.Union[bytes, bytearray, None, list[int]] = None,
            crc_func: typing.Optional[typing.Callable] = None,
            additional_wait_time_for_response: typing.Optional[float] = None,
    ):
        self.address = address
        self.request_id = request_id
        self.sequence_id = sequence_id
        self.data = bytes(data) if data is not None else None
        self.crc_func = crc_func if crc_func else crc.default_vrc_t70_crc()
        self.additional_wait_time_for_response = additional_wait_time_for_response

    def __bytes__(self):
        """
        Serializes request to bytes. When executed all fields need to have values assigned
        """
        if self.address is None:
            raise exceptions.ErrorValueError("Address need to be specified before sending request")

        if self.sequence_id is None:
            raise exceptions.ErrorValueError("Sequence id need to be specified before sending request")

        data_length = len(self.data) if self.data else 0

        res = bytearray(
            [
                self.address & 0xff,
                self.request_id & 0xff,
                (self.sequence_id & 0xff00) >> 8,
                self.sequence_id & 0xff,
                data_length & 0xff
            ]
        )

        if self.data:
            res.extend(self.data)

        crc = self.crc_func(res)
        res.append(crc & 0xff)

        return bytes(res)

    def __len__(self):
        """
        Returns length of serializes request
        """
        data_length = len(self.data) if self.data else 0
        # 1 byte - address,
        # 1 byte - request id,
        # 2 bytes - sequence id,
        # 1 byte - data length,
        # N bytes data,
        # 1 byte - crc8
        return 1 + 1 + 2 + 1 + data_length + 1

    def serialize(self) -> bytes:
        """
        Returns serialized request. Alias to __bytes__ call
        """
        return bytes(self)
