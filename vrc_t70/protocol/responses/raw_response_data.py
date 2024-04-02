import dataclasses
import typing

from vrc_t70 import exceptions
from vrc_t70.crc import default_crc


@dataclasses.dataclass(frozen=True)
class RawResponseData:
    """
    Represents raw response information deserialized from response of VRC-T70 controller
    """
    address: int
    event_id: int
    sequence_id: int
    processing_result: int
    data_length: int
    crc: int
    payload: typing.Optional[bytes] = None


def deserialize(
        data: bytes,
        crc_func: typing.Optional[typing.Callable] = None
) -> RawResponseData:
    """
    Decodes bytes received from controller as response and returns instance of RawResponseData().
    Raises exceptions in case of problems during deserialization.
    """
    if not data:
        raise exceptions.ErrorEmptyResponse()

    crc_func = crc_func if crc_func else default_crc.default_vrc_t70_crc()
    crc = crc_func(data[:-1])

    if crc != data[-1]:
        raise exceptions.ErrorWrongCrc("Wrong CRC in response")

    sequence_id = (data[0x02] << 8) | data[0x03]

    data_length = data[0x05]
    expected_payload_length = len(data) - 7
    if expected_payload_length != data_length:
        raise exceptions.ErrorWrongPayloadLength(
            f"Wrong payload length, expected {expected_payload_length}, received {data_length}"
        )

    payload = bytes(data[0x06:0x06 + data_length]) if data_length else None

    return RawResponseData(
        address=data[0x00],
        event_id=data[0x01],
        sequence_id=sequence_id,
        processing_result=data[0x04],
        data_length=data_length,
        payload=payload,
        crc=data[-1]
    )
