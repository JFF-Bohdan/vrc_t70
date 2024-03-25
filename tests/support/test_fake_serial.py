from tests.support import fake_serial


def test_no_matter_what_will_return_mocked_responses():
    data = [bytes([0x42]), bytes([0x43]), bytes([0x44]), bytes([0x45]), bytes([0x46]), bytes([0x47]), bytes([0x48])]
    fake_port = fake_serial.FakeSerial(responses=data)

    data_received = bytes()
    for index in range(7):
        partial_data = fake_port.read(100 - index)
        data_received += partial_data

    assert data_received == bytes([0x42, 0x43, 0x44, 0x45, 0x46, 0x47, 0x48])
    assert fake_port.read_calls_qty == 7


def test_tracks_all_writes():
    fake_port = fake_serial.FakeSerial(responses=None)
    fake_port.write(bytes([0x01, 0x02, 0x03]))
    fake_port.write(bytes([0x04, 0x05, 0x07]))
    fake_port.write(bytes([0x07, 0x08]))
    fake_port.write(bytes([0x09, 0x10]))

    expected_result = [
        bytes([0x01, 0x02, 0x03]),
        bytes([0x04, 0x05, 0x07]),
        bytes([0x07, 0x08]),
        bytes([0x09, 0x10]),
    ]
    assert fake_port.written_data == expected_result
    assert fake_port.write_calls_qty == 4


def test_tracks_flush_calls_qty():
    fake_port = fake_serial.FakeSerial(responses=None)
    fake_port.flush()
    fake_port.flush()
    fake_port.flush()

    assert fake_port.flush_call_qty == 3
