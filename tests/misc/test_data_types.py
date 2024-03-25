from vrc_t70.protocol import error_codes


def test_error_codes_not_empty():
    assert error_codes.ErrorCodes.all_known_codes()
