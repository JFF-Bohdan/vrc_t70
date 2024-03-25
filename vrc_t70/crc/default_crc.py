import typing

import crcmod


def default_vrc_t70_crc() -> typing.Callable:
    return crcmod.mkCrcFun(poly=0x1D5, initCrc=0, rev=False, xorOut=0)
