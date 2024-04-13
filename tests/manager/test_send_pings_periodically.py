from unittest import mock

from tests.manager import shared as manager_tests_shared

import time_machine

from vrc_t70 import controller_manager, shared
from vrc_t70.protocol.responses.typed import data_types


@time_machine.travel(123000 + 750)
def test_rescans_temperature_on_trunks_periodically(caplog):
    fake_communicator = mock.MagicMock()
    fake_communicator.address = 8

    temperatures_on_trunk_response = []
    for trunk_number in shared.trunks_indexes():
        temperatures_on_trunk_response.append(
            [
                data_types.SensorTemperatureInfo(
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

    options = controller_manager.VrcT70ManagerOptions(
        interval_between_pings=500,
        interval_between_temperatures_refresh=2000,
        missed_communications_count_before_disconnect=10,
    )

    test_manager = controller_manager.VrcT70Manager(
        communicator=fake_communicator,
        options=options,
        events_handler=controller_manager.VrcT70ManagerEventsHandler(),
    )
    test_manager.context = prepared_context
    test_manager.communicate()

    # Has no intentions to perform any communication in future
    tasks_info = manager_tests_shared.extract_tasks_info(test_manager)
    assert set(tasks_info.temperatures_trunks) == set()
    assert set(tasks_info.addresses_trunks) == set()
    assert set(tasks_info.rescan_trunks) == set()

    # calls_for_all_trunks = [mock.call(trunk_number=trunk_number) for trunk_number in shared.trunks_indexes()]

    # Pinged controlled and didn't do anything else
    fake_communicator.ping.assert_called_once()

    fake_communicator.get_temperature_of_sensors_on_trunk.assert_not_called()
    fake_communicator.rescan_sensors_on_trunk.assert_not_called()
    fake_communicator.get_sensors_unique_address_on_trunk.assert_not_called()
    fake_communicator.set_session_id.assert_not_called()
