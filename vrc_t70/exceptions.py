class ErrorBaseVrcT70(Exception):
    """
    Base class for VRC-T70 exceptions
    """
    pass


class ErrorValueError(ErrorBaseVrcT70):
    """
    Received wrong value
    """
    pass


class ErrorParsingResponse(ErrorBaseVrcT70):
    """
    Error when parsing response
    """
    pass


class ErrorWrongCrc(ErrorParsingResponse):
    """
    Response contains wrong CRC
    """
    pass


class ErrorWrongPayloadLength(ErrorParsingResponse):
    """
    Response is malformed and contains wrong payload length
    """
    pass


class ErrorEmptyResponse(ErrorParsingResponse):
    """
    Empty response, nothing to parse
    """
    pass


class ErrorUnknownResponse(ErrorParsingResponse):
    """
    Unknown response
    """
    pass


class ErrorReadingResponse(ErrorBaseVrcT70):
    """
    Error reading resposne from controller
    """
    pass


class ErrorNoResponseFromController(ErrorBaseVrcT70):
    """
    There is no response from controller
    """
    pass


class ErrorResponseFromControllerWithWrongAddress(ErrorBaseVrcT70):
    """
    Received response from controller with wrong address
    """
    def __init__(self, message, unexpected_address: int, expected_address: int):
        super().__init__(message)
        self.unexpected_address = unexpected_address
        self.expected_address = expected_address
