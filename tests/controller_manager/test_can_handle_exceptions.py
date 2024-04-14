from unittest import mock

import time_machine

from vrc_t70 import controller_manager, exceptions
from vrc_t70.controller_manager import context


# @time_machine.travel(123000)
def test_can_handle_no_response_error():
    fake_communicator = mock.MagicMock()

    def raise_no_connection_exception(*args, **kwargs):
        raise exceptions.ErrorNoResponseFromController()

    fake_communicator.set_session_id.side_effect = raise_no_connection_exception

    prepared_context = context.VrcT70ManagerContext()

    test_manager = controller_manager.VrcT70Manager(
        communicator=fake_communicator,
        options=controller_manager.VrcT70ManagerOptions(),
        events_handler=controller_manager.VrcT70ManagerEventsHandler(),
    )
    test_manager.context = prepared_context
    test_manager.communicate()


# @time_machine.travel(123000)
def test_can_handle_base_vrc_ty70_exception():
    fake_communicator = mock.MagicMock()

    def raise_no_connection_exception(*args, **kwargs):
        raise exceptions.ErrorBaseVrcT70()

    fake_communicator.set_session_id.side_effect = raise_no_connection_exception

    prepared_context = context.VrcT70ManagerContext()

    test_manager = controller_manager.VrcT70Manager(
        communicator=fake_communicator,
        options=controller_manager.VrcT70ManagerOptions(),
        events_handler=controller_manager.VrcT70ManagerEventsHandler(),
    )
    test_manager.context = prepared_context
    test_manager.communicate()


@time_machine.travel(123000)
def test_sends_not_connected_event():
    fake_communicator = mock.MagicMock()
    fake_communicator.address = 8

    def raise_no_connection_exception(*args, **kwargs):
        raise exceptions.ErrorBaseVrcT70()

    fake_communicator.set_session_id.side_effect = raise_no_connection_exception

    prepared_context = context.VrcT70ManagerContext()
    prepared_options = controller_manager.VrcT70ManagerOptions(missed_communications_count_before_disconnect=2)
    events_handler = mock.MagicMock()

    test_manager = controller_manager.VrcT70Manager(
        communicator=fake_communicator,
        options=prepared_options,
        events_handler=events_handler,
    )
    test_manager.context = prepared_context
    for _ in range(5):
        test_manager.communicate()

    events_handler.controller_disconnected.assert_called_once_with(8)
