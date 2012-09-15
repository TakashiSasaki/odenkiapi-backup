from __future__ import unicode_literals, print_function
from google.appengine.ext.webapp import Request
from logging import error, debug
from lib.json import JsonRpcError
from encodings.base64_codec import base64_decode
from json import loads

class JsonRpcRequest(object):
    """JSON-RPC 2.0 over HTTP GET method should have method,id and params in URL parameter part.
    params should be encoded in BASE64.
    This method also accepts bare parameters in URL parameter part and puts them in value of 
    'param' key in JSON-RPC request object.
    See http://www.simple-is-better.org/json-rpc/jsonrpc20-over-http.html
    """
    __slots__ = ["jsonrpc", "method", "id", "params", "extra", "error", "pathInfo"]

    def __init__(self, request):
        assert isinstance(request, Request)
        self.error = None
        self.method = None
        self.params = []
        self.id = None
        self.jsonrpc = None
        self.extra = {}
        self.pathInfo = request.path_info.split("/")


        # methods are listed in http://www.w3.org/Protocols/rfc2616/rfc2616-sec9.html
        # default JSON-RPC method is identical to HTTP method and it should be overridden
        self.method = request.method
        if request.method == "OPTIONS":
            self._getFromArguments(request)
            return
        if request.method == "GET":
            self._getFromArguments(request)
            return
        if request.method == "HEAD":
            self._getFromArguments(request)
            return
        if request.method == "POST":
            self._getFromBody(request)
            return
        if request.method == "PUT":
            self._getFromBody(request)
            return
        if request.method == "DELETE":
            self._getFromArguments(request)
            return
        if request.method == "TRACE":
            self._getFromBody(request)
            return
        
    def _getFromArguments(self, request):
        for argument in request.arguments():
            values = request.get_all(argument)
            if argument == "jsonrpc":
                assert len(values) != 0
                if len(values) > 1:
                    error("multiple jsonrpc version indicator")
                    self.error = JsonRpcError.INVALID_REQUEST
                    return
                self.jsonrpc = values[0]
                continue
            if argument == "method":
                debug("argument %s has %s" % (argument, values))
                assert len(values) != 0
                if len(values) > 1:
                    error("multiple methods are given")
                    self.error = JsonRpcError.INVALID_REQUEST
                    return
                self.method = values[0]
                continue
            if argument == "id":
                debug("argument %s has %s" % (argument, values))
                assert len(values) != 0
                if len(values) > 1:
                    error("multiple ids are given")
                    self.error = JsonRpcError.INVALID_REQUEST
                    return
                self.id = values[0]
                continue
            if argument == "params":
                for params in values:
                    try:
                        decoded_params = base64_decode(params)
                    except:
                        error("failed to decode BASE64 for params")
                        self.error = JsonRpcError.PARSE_ERROR
                        return
                    try:
                        loaded_params = loads(decoded_params)
                    except:
                        error("failed to decode JSON for params")
                        self.error = JsonRpcError.PARSE_ERROR
                        return
                    try:
                        assert isinstance(loaded_params, list)
                    except:
                        error("params is expected to be an array of objects, that is, a list")
                        self.error = JsonRpcError.PARSE_ERROR
                    self.params.extend(loaded_params)
                continue
            self.extra[argument] = values
        assert not isinstance(self.id, list)
        #self.extras.extends(extras_in_arguments)
                    
    def _getFromBody(self, request):
        """JSON-RPC request in HTTP body precedes that in parameter part of URL and FORM"""
        assert self.error is None
        assert isinstance(request.body, str)
        try:
            json_rpc_request_dict = loads(request.body)
        except:
            error("failed to parse JSON object in the body")
            self.error = JsonRpcError.PARSE_ERROR
            return
        for k, v in json_rpc_request_dict:
            if k == "jsonrpc":
                self.jsonrpc = v
            if k == "method":
                self.method = v
            if k == "id":
                self.id = v
            if k == "params":
                self.params = v
            self.extra[k] = v
            
    def getValue(self, key):
        params = getattr(self, "params", None)
        if isinstance(params, dict):
            value = params.get(key)
            if value: return value
        extra = getattr(self, "extra", None)
        if isinstance(extra, dict):
            return extra.get(key)

    def getExtra(self):
        if hasattr(self, "extra"): return self.extra
        return None

    def getJsonRpcVersion(self):
        if hasattr(self, "jsonrpc"): return self.jsonrpc
        return 1.0
    
    def getParams(self):
        if hasattr(self, "params"): return self.params
        return None
        
    def getId(self):
        return getattr(self, "id", None)

    def getPathInfo(self, index=None):
        if index:
            assert isinstance(index, int)
            return getattr(self, "pathInfo")[index]
        return getattr(self, "pathInfo", None)
