from vrc_t70.cli_tools import find_controllers


def test_callable():
    assert callable(find_controllers.find_controllers)
