from unittest import mock

from tests.controller_manager import shared as manager_tests_shared

import time_machine

from vrc_t70 import controller_manager, shared
from vrc_t70.protocol import responses


@time_machine.travel(123000 + 2 * controller_manager.DEFAULT_INTERVAL_FOR_TEMPERATURE_REFRESH)
def test_rescans_temperature_on_trunks_periodically():
    fake_communicator = mock.MagicMock()
    fake_communicator.address = 8

    temperatures_on_trunk_response = []
    for trunk_number in shared.trunks_indexes():
        temperatures_on_trunk_response.append(
            [
                responses.data_types.SensorTemperatureInfo(
                    trunk_number=trunk_number,
                    sensor_index=0,
                    is_connected=True,
                    temperature=20 + trunk_number,
                )
            ]
        )
    fake_communicator.get_temperature_of_sensors_on_trunk.side_effect = temperatures_on_trunk_response

    prepared_context = manager_tests_shared.prepare_context_with_all_data()
    assert prepared_context.has_data_for_all_trunks()

    test_manager = controller_manager.VrcT70Manager(
        communicator=fake_communicator,
        options=controller_manager.VrcT70ManagerOptions(),
        events_handler=controller_manager.VrcT70ManagerEventsHandler(),
    )
    test_manager.context = prepared_context
    test_manager.communicate()

    # Has no intentions to perform any communication in future
    tasks_info = manager_tests_shared.extract_tasks_info(test_manager)
    assert set(tasks_info.temperatures_trunks) == set()
    assert set(tasks_info.addresses_trunks) == set()
    assert set(tasks_info.rescan_trunks) == set()

    calls_for_all_trunks = [mock.call(trunk_number=trunk_number) for trunk_number in shared.trunks_indexes()]

    # Requested temperatures on all trunks and nothing more
    fake_communicator.get_temperature_of_sensors_on_trunk.assert_has_calls(calls_for_all_trunks)
    fake_communicator.rescan_sensors_on_trunk.assert_not_called()
    fake_communicator.get_sensors_unique_address_on_trunk.assert_not_called()
    fake_communicator.set_session_id.assert_not_called()
    fake_communicator.ping.assert_not_called()


@time_machine.travel(123000)
def test_dont_send_any_packets_if_communicated_recently():
    fake_communicator = mock.MagicMock()
    fake_communicator.address = 8

    temperatures_on_trunk_response = []
    for trunk_number in shared.trunks_indexes():
        temperatures_on_trunk_response.append(
            [
                responses.data_types.SensorTemperatureInfo(
                    trunk_number=trunk_number,
                    sensor_index=0,
                    is_connected=True,
                    temperature=20 + trunk_number,
                )
            ]
        )
    fake_communicator.get_temperature_of_sensors_on_trunk.side_effect = temperatures_on_trunk_response

    prepared_context = manager_tests_shared.prepare_context_with_all_data()
    assert prepared_context.has_data_for_all_trunks()

    test_manager = controller_manager.VrcT70Manager(
        communicator=fake_communicator,
        options=controller_manager.VrcT70ManagerOptions(),
        events_handler=controller_manager.VrcT70ManagerEventsHandler(),
    )
    test_manager.context = prepared_context
    test_manager.communicate()

    # Has no intentions to perform any communication in future
    tasks_info = manager_tests_shared.extract_tasks_info(test_manager)
    assert set(tasks_info.temperatures_trunks) == set()
    assert set(tasks_info.addresses_trunks) == set()
    assert set(tasks_info.rescan_trunks) == set()

    # Didn't communicate at all
    fake_communicator.get_temperature_of_sensors_on_trunk.assert_not_called()
    fake_communicator.rescan_sensors_on_trunk.assert_not_called()
    fake_communicator.get_sensors_unique_address_on_trunk.assert_not_called()
    fake_communicator.set_session_id.assert_not_called()
    fake_communicator.ping.assert_not_called()
