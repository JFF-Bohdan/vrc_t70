import enum


class ErrorCodes(enum.IntEnum):
    NO_ERROR = 0x00
    UNKNOWN_REQUEST = 0x01
    ACCESS_DENIED = 0x02
    INCORRECT_VALUE = 0x03
    DS18B20_ERROR = 0x04
    DS18B20_BUSY = 0x05

    @staticmethod
    def all_known_codes() -> list[int]:
        return [e.value for e in ErrorCodes]
