from contextlib import contextmanager
from unittest import mock

import time_machine


@contextmanager
def monotonic_clock_shifter(destination, *args, **kwargs):
    assert isinstance(destination, int) or isinstance(destination, float)

    tick = kwargs.get("tick", True)
    tick_delta = kwargs.get("tick_delta", 0.500)
    current_monotonic_time_value = destination

    def mocked_monotonic_implementation() -> float:
        nonlocal current_monotonic_time_value
        result = current_monotonic_time_value

        if tick:
            current_monotonic_time_value += tick_delta

        return result

    with time_machine.travel(destination, *args, **kwargs), \
            mock.patch("time.monotonic", side_effect=mocked_monotonic_implementation), \
            mock.patch(
                "time.monotonic_ns",
                side_effect=lambda: int(10_000_000_000 * mocked_monotonic_implementation())
            ):

        yield
