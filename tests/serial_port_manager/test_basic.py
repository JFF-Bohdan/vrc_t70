from unittest import mock

import serial

from vrc_t70 import serial_port_manager


def test_can_create_manager():
    port_opener = mock.MagicMock()
    _ = serial_port_manager.SerialPortManager(
        port_opener=port_opener,
        managers_for_controllers=[]
    )

    port_opener.assert_not_called()


def test_can_communicate_when_no_errors():
    port_opener = mock.MagicMock()
    managers = [mock.MagicMock() for _ in range(5)]

    port_manager = serial_port_manager.SerialPortManager(
        port_opener=port_opener,
        managers_for_controllers=managers
    )
    port_manager.communicate(max_time_to_talk=10.0)

    port_opener.assert_called_once()
    for manager_instance in managers:
        manager_instance.communicate.assert_called_once_with(max_time_to_talk=2.0)


def test_can_close_when_never_communicated():
    port_opener = mock.MagicMock()
    managers = []
    port_manager = serial_port_manager.SerialPortManager(
        port_opener=port_opener,
        managers_for_controllers=managers
    )
    port_manager.close()
    port_opener.assert_not_called()


def test_can_close_when_port_already_closed():
    returned_port = mock.MagicMock()
    returned_port.closed = True

    port_opener = mock.MagicMock(return_value=returned_port)
    managers = []

    port_manager = serial_port_manager.SerialPortManager(
        port_opener=port_opener,
        managers_for_controllers=managers
    )

    port_manager.communicate()
    port_manager.close()
    port_opener.assert_called_once()


def test_can_close_when_opened():
    returned_port = mock.MagicMock()
    returned_port.closed = False

    port_opener = mock.MagicMock(return_value=returned_port)
    managers = []

    port_manager = serial_port_manager.SerialPortManager(
        port_opener=port_opener,
        managers_for_controllers=managers
    )

    port_manager.communicate()
    port_manager.close()
    port_opener.assert_called_once()


def test_can_close_when_attempt_raises_exception():
    def raise_serial_port_exception():
        raise serial.SerialException()

    returned_port = mock.MagicMock()
    returned_port.closed = False
    returned_port.close.side_effect = raise_serial_port_exception

    port_opener = mock.MagicMock(return_value=returned_port)
    managers = []

    port_manager = serial_port_manager.SerialPortManager(
        port_opener=port_opener,
        managers_for_controllers=managers
    )

    port_manager.communicate()
    port_manager.close()
    port_opener.assert_called_once()
