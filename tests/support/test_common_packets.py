import inspect
import sys
import typing

from tests.support import ex_time_machine

from vrc_t70 import exceptions
from vrc_t70.crc import default_crc
from vrc_t70.protocol.responses import raw_response_data


def get_variables(module_name) -> list[tuple[str, typing.Any]]:
    """
    Extract just the variable names from a given module

    use dir to extract the names within a module and use
    the inspect module to exclude classes, functions and
    other imported modules
    """

    module = sys.modules[module_name]
    candidates = dir(module)

    variables = []
    for name in candidates:
        obj = getattr(module, name)

        if (
                inspect.isclass(obj) or
                inspect.isfunction(obj) or
                inspect.ismodule(obj) or
                name.startswith("__")
        ):
            continue

        variables.append((name, obj,))

    return variables


def get_all_sample_packets() -> list[tuple[str, bytes]]:
    result = []

    vars = get_variables("tests.support.common_packets")
    for name, var in vars:
        if not isinstance(var, (bytes, bytearray)):
            pass

        result.append((name, bytes(var),))

    return result


@ex_time_machine.travel(123000)
def test_all_sample_packets_has_correct_crc():
    vars = get_all_sample_packets()
    assert len(vars)

    for name, var in vars:
        assert len(var), f"Variable with name {name} is empty"
        expected_crc = default_crc.default_vrc_t70_crc()(var[:-1])
        assert var[-1] == expected_crc, f"Variable with name {name} contains wrong crc"


def test_all_sample_response_packets_are_deserializable():
    vars = get_all_sample_packets()
    assert len(vars)

    for name, var in vars:
        if name.endswith("_REQUEST"):
            continue

        try:
            _ = raw_response_data.deserialize(var)
        except exceptions.ErrorBaseVrcT70:
            assert 0, f"Variable {name} can't be properly deserialized"
