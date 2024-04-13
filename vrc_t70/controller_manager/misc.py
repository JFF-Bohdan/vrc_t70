import random
import typing


def get_random_session_id(forbidden_value: typing.Optional[int] = None) -> int:
    """
    Returns non-zero session id. If forbidden_value is provided,
    will return value which is different from it
    """

    while True:
        result = random.getrandbits(32)
        if not result:
            continue

        if forbidden_value and (result == forbidden_value):
            continue

        break

    return result
