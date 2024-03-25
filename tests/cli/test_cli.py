from vrc_t70.cli_tools import cli


def test_callable():
    assert callable(cli.cli)
