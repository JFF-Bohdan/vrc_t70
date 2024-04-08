import dataclasses
import queue

from tests.support import fake_serial

from vrc_t70 import communicator
from vrc_t70 import manager
from vrc_t70 import shared
from vrc_t70.manager import task_type


@dataclasses.dataclass
class TrunkRelatedRequestInfo:
    priority: int
    trunk_number: int
    additional_sort_attribute: int


@dataclasses.dataclass
class RequestsInfo:
    rescan: list[TrunkRelatedRequestInfo] = dataclasses.field(default_factory=list)
    rescan_trunks: set[int] = dataclasses.field(default_factory=set)

    addresses: list[TrunkRelatedRequestInfo] = dataclasses.field(default_factory=list)
    addresses_trunks: set[int] = dataclasses.field(default_factory=set)

    temperatures: list[TrunkRelatedRequestInfo] = dataclasses.field(default_factory=list)
    temperatures_trunks: set[int] = dataclasses.field(default_factory=set)


def extract_tasks_into_list(tasks: queue.PriorityQueue) -> list[task_type.VrcT70ManagerTask]:
    result = []
    while not tasks.empty():
        result.append(tasks.get(block=False))

    return result


def extract_tasks_info(manager: manager.VrcT70Manager) -> RequestsInfo:
    result = RequestsInfo()
    tasks = extract_tasks_into_list(manager.context.tasks_queue)
    for task in tasks:
        if task.task.func == manager._rescan_sensors_on_trunk_task:
            destination = result.rescan
        elif task.task.func == manager._get_sensors_address_on_trunk_task:
            destination = result.addresses
        elif task.task.func == manager._get_sensors_temperature_on_trunk_task:
            destination = result.temperatures
        else:
            assert False, f"Unexpected task in a queue {task}"

        destination.append(
            TrunkRelatedRequestInfo(
                priority=task.priority,
                trunk_number=task.task.args[0],
                additional_sort_attribute=task.additional_sort_attribute
            )
        )

    result.addresses_trunks = [item.trunk_number for item in result.addresses]
    result.temperatures_trunks = [item.trunk_number for item in result.temperatures]
    result.rescan_trunks = [item.trunk_number for item in result.rescan]

    return result


def test_have_some_correct_addresses_and_no_temperatures():
    all_trunks = set(shared.trunks_indexes())
    test_manager = manager.VrcT70Manager(
        communicator=communicator.VrcT70Communicator(
            port=fake_serial.FakeSerial()
        ),
        options=manager.VrcT70ManagerOptions(),
        events_handler=manager.VrcT70ManagerEventsHandler()
    )

    test_manager.context.expected_sensors_count_on_trunk[1] = 3
    test_manager.context.addresses_on_trunk[1] = [1, 2, 3]

    test_manager.context.expected_sensors_count_on_trunk[2] = 4
    test_manager.context.addresses_on_trunk[2] = [4, 5, 6, 7]

    test_manager.context.expected_sensors_count_on_trunk[5] = 1
    test_manager.context.addresses_on_trunk[5] = [8]

    test_manager._request_update_info_on_trunks()
    tasks_info = extract_tasks_info(test_manager)

    assert sorted(tasks_info.rescan_trunks) == sorted(list(all_trunks - {1, 2, 5}))
    assert sorted(tasks_info.temperatures_trunks) == [1, 2, 5]
    assert tasks_info.addresses_trunks == []


def test_have_unexpected_number_of_addresses_and_no_temperatures():
    all_trunks = set(shared.trunks_indexes())
    test_manager = manager.VrcT70Manager(
        communicator=communicator.VrcT70Communicator(
            port=fake_serial.FakeSerial()
        ),
        options=manager.VrcT70ManagerOptions(),
        events_handler=manager.VrcT70ManagerEventsHandler()
    )

    test_manager.context.expected_sensors_count_on_trunk[1] = 42
    test_manager.context.addresses_on_trunk[1] = [1, 2, 3]

    test_manager.context.expected_sensors_count_on_trunk[2] = 123
    test_manager.context.addresses_on_trunk[2] = [4, 5, 6, 7]

    test_manager.context.expected_sensors_count_on_trunk[5] = 45
    test_manager.context.addresses_on_trunk[5] = [8]

    test_manager._request_update_info_on_trunks()
    tasks_info = extract_tasks_info(test_manager)

    assert sorted(tasks_info.rescan_trunks) == sorted(all_trunks)
    assert tasks_info.temperatures_trunks == []
    assert tasks_info.addresses_trunks == []


def test_have_some_none_addresses_and_no_temperatures():
    all_trunks = set(shared.trunks_indexes())
    test_manager = manager.VrcT70Manager(
        communicator=communicator.VrcT70Communicator(
            port=fake_serial.FakeSerial()
        ),
        options=manager.VrcT70ManagerOptions(),
        events_handler=manager.VrcT70ManagerEventsHandler()
    )

    test_manager.context.expected_sensors_count_on_trunk[1] = 3
    test_manager.context.addresses_on_trunk[1] = [1, None, 3]

    test_manager.context.expected_sensors_count_on_trunk[2] = 4
    test_manager.context.addresses_on_trunk[2] = [4, 5, None, 7]

    test_manager.context.expected_sensors_count_on_trunk[5] = 3
    test_manager.context.addresses_on_trunk[5] = [8, 9, 10]

    test_manager._request_update_info_on_trunks()
    tasks_info = extract_tasks_info(test_manager)

    assert sorted(tasks_info.rescan_trunks) == sorted(list(all_trunks - {5}))
    assert sorted(tasks_info.temperatures_trunks) == [5]
    assert tasks_info.addresses_trunks == []


def test_have_temperatures_but_no_addresses():
    all_trunks = set(shared.trunks_indexes())
    test_manager = manager.VrcT70Manager(
        communicator=communicator.VrcT70Communicator(
            port=fake_serial.FakeSerial()
        ),
        options=manager.VrcT70ManagerOptions(),
        events_handler=manager.VrcT70ManagerEventsHandler()
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
    tasks_info = extract_tasks_info(test_manager)

    assert sorted(tasks_info.temperatures_trunks) == [5]
    assert sorted(tasks_info.addresses_trunks) == [4]
    assert sorted(tasks_info.rescan_trunks) == sorted(list(all_trunks - {1, 2, 4, 5}))
