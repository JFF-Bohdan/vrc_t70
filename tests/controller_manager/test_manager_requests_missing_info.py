from tests.controller_manager import shared as manager_tests_shared
from tests.support import fake_serial

from vrc_t70 import controller_communicator, controller_manager, shared


def test_have_some_correct_addresses_and_no_temperatures():
    all_trunks = set(shared.trunks_indexes())
    test_manager = controller_manager.VrcT70Manager(
        communicator=controller_communicator.VrcT70Communicator(
            port=fake_serial.FakeSerial()
        ),
        options=controller_manager.VrcT70ManagerOptions(),
        events_handler=controller_manager.VrcT70ManagerEventsHandler()
    )

    test_manager.context.expected_sensors_count_on_trunk[1] = 3
    test_manager.context.addresses_on_trunk[1] = [1, 2, 3]

    test_manager.context.expected_sensors_count_on_trunk[2] = 4
    test_manager.context.addresses_on_trunk[2] = [4, 5, 6, 7]

    test_manager.context.expected_sensors_count_on_trunk[5] = 1
    test_manager.context.addresses_on_trunk[5] = [8]

    test_manager._request_update_info_on_trunks()
    tasks_info = manager_tests_shared.extract_tasks_info(test_manager)

    assert sorted(tasks_info.rescan_trunks) == sorted(list(all_trunks - {1, 2, 5}))
    assert sorted(tasks_info.temperatures_trunks) == [1, 2, 5]
    assert tasks_info.addresses_trunks == []


def test_have_unexpected_number_of_addresses_and_no_temperatures():
    all_trunks = set(shared.trunks_indexes())
    test_manager = controller_manager.VrcT70Manager(
        communicator=controller_communicator.VrcT70Communicator(
            port=fake_serial.FakeSerial()
        ),
        options=controller_manager.VrcT70ManagerOptions(),
        events_handler=controller_manager.VrcT70ManagerEventsHandler()
    )

    test_manager.context.expected_sensors_count_on_trunk[1] = 42
    test_manager.context.addresses_on_trunk[1] = [1, 2, 3]

    test_manager.context.expected_sensors_count_on_trunk[2] = 123
    test_manager.context.addresses_on_trunk[2] = [4, 5, 6, 7]

    test_manager.context.expected_sensors_count_on_trunk[5] = 45
    test_manager.context.addresses_on_trunk[5] = [8]

    test_manager._request_update_info_on_trunks()
    tasks_info = manager_tests_shared.extract_tasks_info(test_manager)

    assert sorted(tasks_info.rescan_trunks) == sorted(all_trunks)
    assert tasks_info.temperatures_trunks == []
    assert tasks_info.addresses_trunks == []


def test_have_some_none_addresses_and_no_temperatures():
    all_trunks = set(shared.trunks_indexes())
    test_manager = controller_manager.VrcT70Manager(
        communicator=controller_communicator.VrcT70Communicator(
            port=fake_serial.FakeSerial()
        ),
        options=controller_manager.VrcT70ManagerOptions(),
        events_handler=controller_manager.VrcT70ManagerEventsHandler()
    )

    test_manager.context.expected_sensors_count_on_trunk[1] = 3
    test_manager.context.addresses_on_trunk[1] = [1, None, 3]

    test_manager.context.expected_sensors_count_on_trunk[2] = 4
    test_manager.context.addresses_on_trunk[2] = [4, 5, None, 7]

    test_manager.context.expected_sensors_count_on_trunk[5] = 3
    test_manager.context.addresses_on_trunk[5] = [8, 9, 10]

    test_manager._request_update_info_on_trunks()
    tasks_info = manager_tests_shared.extract_tasks_info(test_manager)

    assert sorted(tasks_info.rescan_trunks) == sorted(list(all_trunks - {5}))
    assert sorted(tasks_info.temperatures_trunks) == [5]
    assert tasks_info.addresses_trunks == []


def test_have_temperatures_but_no_addresses():
    all_trunks = set(shared.trunks_indexes())
    test_manager = controller_manager.VrcT70Manager(
        communicator=controller_communicator.VrcT70Communicator(
            port=fake_serial.FakeSerial()
        ),
        options=controller_manager.VrcT70ManagerOptions(),
        events_handler=controller_manager.VrcT70ManagerEventsHandler()
    )

    test_manager.context.expected_sensors_count_on_trunk[1] = 3
    test_manager.context.addresses_on_trunk[1] = [1, 2, 3]

    test_manager.context.expected_sensors_count_on_trunk[2] = 4
    test_manager.context.addresses_on_trunk[2] = [4, 5, 6, 7]

    test_manager.context.expected_sensors_count_on_trunk[5] = 1
    test_manager.context.addresses_on_trunk[5] = [8]

    test_manager.context.temperatures_on_trunk[1] = [20, 21, 22]
    test_manager.context.temperatures_on_trunk[2] = [40, 50, 60]
    test_manager.context.temperatures_on_trunk[4] = [1, 2, 3]

    test_manager._request_update_info_on_trunks()
    tasks_info = manager_tests_shared.extract_tasks_info(test_manager)

    assert sorted(tasks_info.temperatures_trunks) == [5]
    assert sorted(tasks_info.addresses_trunks) == [4]
    assert sorted(tasks_info.rescan_trunks) == sorted(list(all_trunks - {1, 2, 4, 5}))
