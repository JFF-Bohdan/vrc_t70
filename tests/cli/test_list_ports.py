from vrc_t70.cli_tools import list_ports


def test_callable():
    assert callable(list_ports.list_ports)
