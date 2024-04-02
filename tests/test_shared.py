import math

import pytest

from vrc_t70 import shared


@pytest.mark.parametrize(
    "data, expected",
    [
        (bytes([0x55, 0xd5, 0x9f, 0x41]), 19.9792),
        (bytes([0x00, 0x80, 0xa7, 0x41]), 20.94),
        (bytes([0x00, 0x80, 0xa7, 0x41]), 20.94),
        (bytes([0x00, 0x80, 0x93, 0x41]), 18.44),
        (bytes([0x00, 0x00, 0x9d, 0x41]), 19.62),
    ]
)
def test_decode_float(data, expected):
    calculated, = shared.decode_float(data)
    assert math.isclose(calculated, expected, abs_tol=0.01)
