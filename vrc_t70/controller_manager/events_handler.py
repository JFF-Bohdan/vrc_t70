class VrcT70ManagerEventsHandler:
    """
    Base event handler. To receive information about events please override methods with necessary
    logic and pass instance of a handler to a manager
    """
    def controller_connected(self, controller_address: int) -> None:
        pass  # pragma: no cover

    def controller_disconnected(self, controller_address: int) -> None:
        pass  # pragma: no cover

    def number_of_sensors_on_trunk_received(
            self,
            controller_address: int,
            trunk_number: int,
            sensors_count: int
    ) -> None:
        pass  # pragma: no cover

    def address_of_sensors_received_on_trunk(
            self,
            controller_address: int,
            trunk_number: int,
            addresses: list[int | None],
    ):
        pass  # pragma: no cover

    def temperature_of_sensors_received(
            self,
            controller_address: int,
            trunk_number: int,
            temperatures: list[float | None],
    ):
        pass  # pragma: no cover
