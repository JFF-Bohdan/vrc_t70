from vrc_t70.protocol.responses import raw_response_data


class BaseResponse:
    """
    Base class used to represent response from VRC-T70 controller
    """
    def __init__(
            self,
            raw_response: raw_response_data.RawResponseData
    ):
        self.raw_response = raw_response
