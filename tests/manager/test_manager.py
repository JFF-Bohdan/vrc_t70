from tests.support import fake_serial

from vrc_t70 import communicator
from vrc_t70 import manager


def test_can_create_manager():
    _ = manager.VrcT70Manager(
        communicator=communicator.VrcT70Communicator(
            port=fake_serial.FakeSerial()
        ),
        options=manager.VrcT70ManagerOptions(),
        events_handler=manager.VrcT70ManagerEventsHandler()
    )
