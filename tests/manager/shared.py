import dataclasses
import queue

from vrc_t70 import manager, shared
from vrc_t70.manager import context, task_type


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


def prepare_context_with_all_data(
        last_communication_time: float = 123000,
        last_temperature_request_on_trunks=123000
) -> context.VrcT70ManagerContext:
    result = context.VrcT70ManagerContext()

    result.last_communication_time = last_communication_time
    result.session_id = 0x2233

    for trunk_number in shared.trunks_indexes():
        result.expected_sensors_count_on_trunk = 1

        sensor_address = 10 + trunk_number
        result.addresses_on_trunk[trunk_number][0] = sensor_address

        sensor_temperature = 30 + trunk_number
        result.temperatures_on_trunk[trunk_number][0] = sensor_temperature

        result.full_sensor_info[sensor_address] = shared.FullSensorInfo(
            trunk_number=trunk_number,
            sensor_index=0,
            address=sensor_address,
            has_error=False,
            temperature=sensor_temperature
        )
        result.timestamp_temperature_refresh_on_trunk[trunk_number] = last_temperature_request_on_trunks

    return result
