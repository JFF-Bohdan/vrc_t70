import dataclasses
import enum
import typing


class VrcT70ManagerTaskPriority(enum.IntEnum):
    HIGH = 0
    MEDIUM = 5
    LOW = 10
    ULTRA_LOW = 50


@dataclasses.dataclass(order=True)
class VrcT70ManagerTask:
    priority: int
    task: typing.Callable = dataclasses.field(compare=False)
    additional_sort_attribute: int = 0
