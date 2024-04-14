from vrc_t70.protocol import responses


def test_can_deserialize_raw_data():
    raw_bytes = bytes([0x01, 0x01, 0x22, 0x33, 0x00, 0x00, 0x56])
    raw_response = responses.deserialize(raw_bytes)
    response = responses.BaseResponse(raw_response)
    expected_raw_data = responses.RawResponseData(
        address=0x01,
        event_id=0x01,
        sequence_id=0x2233,
        processing_result=0x00,
        data_length=0x00,
        crc=0x56
    )
    assert response.raw_response == expected_raw_data
