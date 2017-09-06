import binascii

from vrc_t70.request import VrcT70Request


def test_ping_request_to_01():
    expected_result = "01012233000A"

    cmd = VrcT70Request(0x01, 0x01, 0x2233)
    cmd = cmd.to_bytearray()

    res = binascii.hexlify(cmd).decode("ascii")

    assert res.lower() == expected_result.lower()


def test_ping_request_to_07():
    expected_result = "070122330014"

    cmd = VrcT70Request(0x07, 0x01, 0x2233)
    cmd = cmd.to_bytearray()

    res = binascii.hexlify(cmd).decode("ascii")

    assert res.lower() == expected_result.lower()


def test_ping_with_fake_payload():
    expected_result = "07012233030102039A"

    cmd = VrcT70Request(0x07, 0x01, 0x2233)
    cmd.data = bytearray([0x01, 0x02, 0x03])
    cmd = cmd.to_bytearray()

    res = binascii.hexlify(cmd).decode("ascii")

    assert res.lower() == expected_result.lower()


def test_convert_to_bytes():
    expected_result = "07012233030102039A"

    cmd = VrcT70Request(0x07, 0x01, 0x2233)
    cmd.data = bytearray([0x01, 0x02, 0x03])
    cmd = bytes(cmd)

    res = binascii.hexlify(cmd).decode("ascii")

    assert res.lower() == expected_result.lower()

