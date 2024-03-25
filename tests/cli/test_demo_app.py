from vrc_t70.cli_tools import demo_app


def test_callable():
    assert callable(demo_app.demo_app)
