from __future__ import unicode_literals, print_function
class JsonRpcError(object):
    PARSE_ERROR = -32700
    INVALID_REQUEST = -32600
    METHOD_NOT_FOUND = -32601
    INVALID_PARAMS = -32602
    INTERNAL_ERROR = -32603
    SERVER_ERROR_RESERVED_MAX = -32000
    SERVER_ERROR_RESERVED_MIN = -32099

class JsonRpcException(RuntimeError):
    def __init__(self, code, message, data):
        RuntimeError.__init__(self)
        self.code = code
        self.message = message
        self.data = data

    def __str__(self):
        return unicode(self.message) + unicode(self.data)
