from unittest import mock

from vrc_t70 import limitations
from vrc_t70.controller_manager.misc import get_random_session_id


def test_generates_valid_session_id():
    value = get_random_session_id()
    assert (value >= limitations.MIN_SESSION_ID) and (value <= limitations.MAX_SESSION_ID)


@mock.patch("vrc_t70.controller_manager.misc.random.getrandbits", side_effect=[0, 0, 42])
def test_would_not_return_zero(mocked_getrandbits):
    value = get_random_session_id()

    assert value == 42
    mocked_getrandbits.assert_has_calls([mock.call(32), mock.call(32), mock.call(32)])


@mock.patch("vrc_t70.controller_manager.misc.random.getrandbits", side_effect=[123, 123, 42])
def test_would_skip_forbidden_value(mocked_getrandbits):
    value = get_random_session_id(forbidden_value=123)

    assert value == 42
    mocked_getrandbits.assert_has_calls([mock.call(32), mock.call(32), mock.call(32)])


@mock.patch("vrc_t70.controller_manager.misc.random.getrandbits", side_effect=[123, 123, 0, 42])
def test_would_skip_forbidden_value_and_zeroes(mocked_getrandbits):
    value = get_random_session_id(forbidden_value=123)

    assert value == 42
    mocked_getrandbits.assert_has_calls([mock.call(32), mock.call(32), mock.call(32), mock.call(32)])
