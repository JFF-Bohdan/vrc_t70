from vrc_t70 import limitations
from vrc_t70 import shared
from vrc_t70.manager import context


def test_can_create_context():
    _ = context.VrcT70ManagerContext()


def test_can_detect_when_do_not_have_all_info():
    test_context = context.VrcT70ManagerContext()

    for trunk_number in range(limitations.MIN_TRUNK_NUMBER, limitations.MAX_TRUNK_NUMBER // 2):
        test_context.addresses_on_trunk[trunk_number] = [1, 2, 3]
        test_context.temperatures_on_trunk[trunk_number] = [1, 2, 3]

    assert test_context.has_data_for_all_trunks() == False  # noqa


def test_can_detect_when_have_all_info():
    test_context = context.VrcT70ManagerContext()

    for trunk_number in range(limitations.MIN_TRUNK_NUMBER, limitations.MAX_TRUNK_NUMBER + 1):
        test_context.addresses_on_trunk[trunk_number] = [1, 2, 3]
        test_context.temperatures_on_trunk[trunk_number] = [1, 2, 3]

    assert test_context.has_data_for_all_trunks() == True  # noqa


def test_can_detect_when_do_not_have_all_info_after_clear():
    test_context = context.VrcT70ManagerContext()

    for trunk_number in range(limitations.MIN_TRUNK_NUMBER, limitations.MAX_TRUNK_NUMBER + 1):
        test_context.addresses_on_trunk[trunk_number] = [1, 2, 3]
        test_context.temperatures_on_trunk[trunk_number] = [1, 2, 3]

    assert test_context.has_data_for_all_trunks() == True  # noqa

    test_context.clear_data_retrieved_from_controller()
    assert test_context.has_data_for_all_trunks() == False  # noqa


def test_can_clear_info_gathered_from_controller():
    test_context = context.VrcT70ManagerContext()

    for trunk_number in range(limitations.MIN_TRUNK_NUMBER, limitations.MAX_TRUNK_NUMBER + 1):
        test_context.addresses_on_trunk[trunk_number] = [1, 2, 3]
        test_context.temperatures_on_trunk[trunk_number] = [1, 2, 3]
        test_context.expected_sensors_count_on_trunk[trunk_number] = 42
        test_context.timestamp_temperature_refresh_on_trunk[trunk_number] = 123

    for fake_address in range(10):
        test_context.full_sensor_info[fake_address] = shared.FullSensorInfo(
            trunk_number=42,
            sensor_index=1,
            address=fake_address
        )

    test_context.clear_data_retrieved_from_controller()

    assert not test_context.expected_sensors_count_on_trunk
    assert not test_context.addresses_on_trunk
    assert not test_context.temperatures_on_trunk
    assert not test_context.timestamp_temperature_refresh_on_trunk
    assert not test_context.full_sensor_info
