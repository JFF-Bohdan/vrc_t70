from vrc_t70 import exceptions
from vrc_t70 import limitations
from vrc_t70.protocol.responses import base_response
from vrc_t70.protocol.responses import raw_response_data


class SetControllerNewAddressResponse(base_response.BaseResponse):
    """
    Response for request to set new controller address
    """
    def __init__(
        self,
        raw_response: raw_response_data.RawResponseData
    ):
        super().__init__(raw_response=raw_response)
        if (not self.raw_response.payload) or (len(self.raw_response.payload) != 1):
            raise exceptions.ErrorWrongPayloadLength()

        self.new_address = self.raw_response.payload[0]
        limitations.validate_controller_address(self.new_address)
