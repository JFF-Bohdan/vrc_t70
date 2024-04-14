from unittest import mock

import serial

from tests.support import ex_time_machine

from vrc_t70 import serial_port_manager


@mock.patch("vrc_t70.serial_port_manager.serial_port_manager.time")
@ex_time_machine.travel(123000)
def test_sleeps_on_single_error(mocked_time):
    def raise_serial_port_exception(max_time_to_talk: float):
        raise serial.SerialException()

    returned_port = mock.MagicMock()
    returned_port.closed = False

    port_opener = mock.MagicMock(return_value=returned_port)

    bad_manager = mock.MagicMock()
    bad_manager.communicate.side_effect = raise_serial_port_exception

    managers = [mock.MagicMock(), mock.MagicMock(), bad_manager, mock.MagicMock(), mock.MagicMock()]
    port_manager = serial_port_manager.SerialPortManager(
        port_opener=port_opener,
        managers_for_controllers=managers,
        sleep_interval_on_error=10,
    )
    port_manager.communicate(max_time_to_talk=20)

    port_opener.assert_called_once()
    returned_port.close.assert_called_once()
    mocked_time.sleep.assert_called_once_with(10)
    managers[0].communicate.assert_called_once_with(max_time_to_talk=4.0)
    managers[1].communicate.assert_called_once_with(max_time_to_talk=4.0)
    managers[2].communicate.assert_called_once_with(max_time_to_talk=4.0)
    managers[3].assert_not_called()
    managers[4].assert_not_called()


@mock.patch("vrc_t70.serial_port_manager.serial_port_manager.time")
@ex_time_machine.travel(123000)
def test_creates_new_port_on_too_many_errors(mocked_time):
    def raise_serial_port_exception(max_time_to_talk: float):
        raise serial.SerialException()

    returned_port = mock.MagicMock()
    returned_port.closed = False

    port_opener = mock.MagicMock(return_value=returned_port)

    bad_manager = mock.MagicMock()
    bad_manager.communicate.side_effect = raise_serial_port_exception

    port_manager = serial_port_manager.SerialPortManager(
        port_opener=port_opener,
        managers_for_controllers=[bad_manager],
        sleep_interval_on_error=10,
        reopen_attempts_count_before_creating_new_port=2,
    )

    for _ in range(5):
        port_manager.communicate()

    # Expected sequence should be
    # 1. Create port instance -> Open port -> Communicate -> Close
    # 2. Open port -> Communicate -> Close
    # 3. Destroy port -> Create port instance -> Open port -> Communicate -> Close
    # 4. Open port -> Communicate -> Close
    # 5. Destroy port -> Create port instance -> Open port -> Communicate -> Close

    port_opener.assert_has_calls([mock.call(), mock.call(), mock.call()])
    returned_port.close.assert_has_calls([mock.call(), mock.call(), mock.call(), mock.call(), mock.call()])
