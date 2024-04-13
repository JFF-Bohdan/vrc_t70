import dataclasses

DEFAULT_INTERVAL_FOR_TEMPERATURE_REFRESH = 10
DEFAULT_INTERVAL_FOR_PING_REQUESTS = 3
DEFAULT_MAX_MISSED_COMMUNICATIONS = 6


@dataclasses.dataclass(frozen=True)
class VrcT70ManagerOptions:
    interval_between_pings: float = DEFAULT_INTERVAL_FOR_PING_REQUESTS
    interval_between_temperatures_refresh: float = DEFAULT_INTERVAL_FOR_TEMPERATURE_REFRESH
    missed_communications_count_before_disconnect: int = DEFAULT_MAX_MISSED_COMMUNICATIONS
