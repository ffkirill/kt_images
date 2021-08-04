from aiohttp.web_response import StreamResponse

class HTTPStreamedException(Exception):
    """Exception class to pass exception from stream response generator"""
    response: StreamResponse
    reason: Exception

    def __init__(self, reason: Exception, response: StreamResponse):
        self.response = response
        self.reason = reason
        super().__init__(reason)