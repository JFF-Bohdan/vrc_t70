from unittest import mock

from tests.support import fake_serial

import time_machine

from vrc_t70 import controller_communicator, controller_manager, shared
from vrc_t70.protocol.responses.typed import data_types


def test_can_create_manager():
    _ = controller_manager.VrcT70Manager(
        communicator=controller_communicator.VrcT70Communicator(
            port=fake_serial.FakeSerial()
        ),
        options=controller_manager.VrcT70ManagerOptions(),
        events_handler=controller_manager.VrcT70ManagerEventsHandler()
    )


@time_machine.travel(12345, tick=True)
@mock.patch("vrc_t70.controller_manager.misc.get_random_session_id", return_value=0xcafebabe)
def test_attempts_to_establish_new_session_id(_mocked_get_random_session_id):
    fake_communicator = mock.MagicMock()
    fake_communicator.set_session_id.return_value = 0xcafebabe

    test_manager = controller_manager.VrcT70Manager(
        communicator=fake_communicator,
        options=controller_manager.VrcT70ManagerOptions(),
        events_handler=controller_manager.VrcT70ManagerEventsHandler()
    )

    test_manager.communicate(max_time_to_talk=0.001)

    fake_communicator.set_session_id.assert_called_once()
    assert test_manager.context.session_id == 0xcafebabe


@time_machine.travel(12345, tick=True)
@mock.patch("vrc_t70.controller_manager.misc.get_random_session_id", return_value=0xcafebabe)
def test_rescans_trunks(_mocked_get_random_session_id):
    fake_communicator = mock.MagicMock()
    fake_communicator.set_session_id.return_value = 0xcafebabe
    fake_communicator.rescan_sensors_on_trunk.return_value = 1

    addresses_on_trunk_response = []
    for trunk_number in shared.trunks_indexes():
        addresses_on_trunk_response.append(
            [
                data_types.SensorAddressInfo(
                    trunk_number=trunk_number,
                    sensor_index=0,
                    is_error_detected=False,
                    address=12345 + trunk_number,
                )
            ]
        )
    fake_communicator.get_sensors_unique_address_on_trunk.side_effect = addresses_on_trunk_response

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

    test_manager = controller_manager.VrcT70Manager(
        communicator=fake_communicator,
        options=controller_manager.VrcT70ManagerOptions(),
        events_handler=controller_manager.VrcT70ManagerEventsHandler()
    )

    test_manager.communicate()

    fake_communicator.set_session_id.assert_called_once()
    calls_for_all_trunks = [mock.call(trunk_number=trunk_number) for trunk_number in shared.trunks_indexes()]

    fake_communicator.rescan_sensors_on_trunk.assert_has_calls(calls_for_all_trunks)
    fake_communicator.get_sensors_unique_address_on_trunk.assert_has_calls(calls_for_all_trunks)
    fake_communicator.get_temperature_of_sensors_on_trunk.assert_has_calls(calls_for_all_trunks)
