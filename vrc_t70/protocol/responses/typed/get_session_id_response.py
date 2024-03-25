from vrc_t70 import exceptions
from vrc_t70.protocol.responses import base_response
from vrc_t70.protocol.responses import raw_response_data


class GetSessionIdResponse(base_response.BaseResponse):
    """
    Response for request of session id
    """
    def __init__(
        self,
        raw_response: raw_response_data.RawResponseData
    ):
        super().__init__(raw_response=raw_response)
        if (not self.raw_response.payload) or (len(self.raw_response.payload) != 4):
            raise exceptions.ErrorWrongPayloadLength()

        self.session_id = self.raw_response.payload[0] << 24
        self.session_id |= self.raw_response.payload[1] << 16
        self.session_id |= self.raw_response.payload[2] << 8
        self.session_id |= self.raw_response.payload[3]
