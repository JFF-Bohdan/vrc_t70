from vrc_t70.protocol.responses import base_response
from vrc_t70.protocol.responses import raw_response_data


def test_can_deserialize_raw_data():
    raw_bytes = bytes([0x01, 0x01, 0x22, 0x33, 0x00, 0x00, 0x56])
    raw_response = raw_response_data.deserialize(raw_bytes)
    response = base_response.BaseResponse(raw_response)
    expected_raw_data = raw_response_data.RawResponseData(
        address=0x01,
        event_id=0x01,
        sequence_id=0x2233,
        processing_result=0x00,
        data_length=0x00,
        crc=0x56
    )
    assert response.raw_response == expected_raw_data
