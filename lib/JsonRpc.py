from encodings.base64_codec import base64_decode
from simplejson import dumps, load, loads, JSONDecodeError
from lib.CachedContent import CachedContent
from logging import debug, getLogger, DEBUG
getLogger().setLevel(DEBUG)


JSON_RPC_ERROR_PARSE_ERROR = -32700
JSON_RPC_ERROR_INVALID_REQUEST = -32600
JSON_RPC_ERROR_METHOD_NOT_FOUND = -32601
JSON_RPC_ERROR_INVALID_PARAMS = -32602
JSON_RPC_ERROR_INTERNAL_ERROR = -32603
JSON_RPC_ERROR_SERVER_ERROR_RESERVED_MAX = -32000
JSON_RPC_ERROR_SERVER_ERROR_RESERVED_MIN = -32099

def toHttpStatus(error_code):
    if error_code == JSON_RPC_ERROR_PARSE_ERROR:
        return 500
    if error_code == JSON_RPC_ERROR_INVALID_REQUEST:
        return 400
    if error_code == JSON_RPC_ERROR_METHOD_NOT_FOUND:
        return 404
    if error_code == JSON_RPC_ERROR_INVALID_PARAMS:
        return 500
    if error_code == JSON_RPC_ERROR_INTERNAL_ERROR:
        return 500
    if error_code >= JSON_RPC_ERROR_SERVER_ERROR_RESERVED_MIN and error_code <= JSON_RPC_ERROR_SERVER_ERROR_RESERVED_MAX:
        return 500
    return None

def getJsonFromUrl(params):
    assert isinstance(params, dict)
    json_from_url = {}
    for k, v in params.items():
        if json_from_url.get(k):
            if isinstance(json_from_url[k], list):
                json_from_url[k].append(v)
            else:
                json_from_url[k] = [json_from_url[k], v]
        else:
            json_from_url[k] = v
    
    base64_params = json_from_url.get("params")
    if base64_params:
        params = base64_decode(base64_params)
    else:
        params = "[]"
    json_from_url["params"] = loads(params)
    return json_from_url
        
def getJsonFromBody(body):
    assert isinstance(body, str)
    json_from_body = loads(body)
    if json_from_body is None:
        json_from_body = {}
    assert isinstance(json_from_body, dict)
    return json_from_body

class JsonRpc(object):
    __slots__ = [ "request", "response", "jsonRequest", "requestHandler", "request", "response", "jsonrpc", "method", "params", "id", "result", "error"]
    
    def __init__(self, request_handler):
        self.requestHandler = request_handler
        self.request = request_handler.request
        self.response = request_handler.response
        self.error = {}
        self.getJsonRequest()
        debug(self.jsonRequest)
        if self.jsonRequest:
            self.jsonrpc = self.jsonRequest.get("jsonrpc", None)
            if isinstance(self.jsonrpc, list) and len(self.jsonrpc) == 1:
                self.jsonrpc = self.jsonrpc[0]
            self.method = self.jsonRequest.get("method", None)
            if isinstance(self.method, list) and len(self.method) == 1:
                self.method = self.method[0]
            self.params = self.jsonRequest.get("params", None)
            if isinstance(self.params, list) and len(self.params) == 1:
                self.params = self.params[0]
            self.id = self.jsonRequest.get("id", None)
            if isinstance(self.id, list) and len(self.id) == 1:
                self.id = self.id[0]
        self.result = None
        
    def setResult(self, result):
        self.result = result
    
    def getArgumentDict(self):
        d = {}
        for a in self.request.arguments():
            assert isinstance(a, unicode)
            d[a] = self.request.get_all(a)
        debug(str(d))
        return d

    def setErrorCode(self, error_code):
        assert isinstance(error_code, int)
        assert isinstance(self.error, dict)
        self.error["code"] = error_code
    
    def getHttpStatus(self):
        try:
            error_code = self.error["code"]
        except Exception, e:
            error_code = JSON_RPC_ERROR_INTERNAL_ERROR
            self.error["code"] = error_code
            self.error["message"] = "Error occured but error code was not set. This is an internal error. " + e.message 
        return toHttpStatus(error_code)
    
    def setErrorMessage(self, error_message):
        assert isinstance(error_message, str)
        self.error["message"] = error_message
    
    def setErrorData(self, error_data):
        self.error["data"] = error_data

    def getJsonRequest(self):
        if hasattr(self, "jsonRequest"):
            return self.jsonRequest
        if self.request.method == "POST" or self.request.method == "PUT":
            # POST can change the state of servers.
            # PUT should be idempotent.
            debug("POST or PUT")
            try:
                self.jsonRequest = getJsonFromBody(self.request.body)
                return
            except JSONDecodeError, e:
                self.jsonRequest = None
                self.setErrorCode(JSON_RPC_ERROR_PARSE_ERROR)
                self.setErrorMessage(e.message)
                return
        if self.request.method == "GET" or self.request.method == "DELETE":
            debug("GET or DELETE")
            # GET should not change the state of servers.
            # DELETE should be idempotent.
            try:
                self.jsonRequest = getJsonFromUrl(self.getArgumentDict())
                assert isinstance(self.jsonRequest, dict)
                return
            except JSONDecodeError, e:
                self.jsonRequest = None
                self.setErrorCode(JSON_RPC_ERROR_PARSE_ERROR)
                self.setErrorMessage(e.message)
                return

        self.jsonRequest = None
        self.setErrorCode(JSON_RPC_ERROR_INVALID_REQUEST)
        self.setErrorMessage("%s is unknown HTTP method" % self.request.method)
        
    def write(self):
        if self.result is None:
            assert isinstance(self.error, dict)
            self.response.content_type = "application/json"
            self.response.set_status(self.getHttpStatus())
            params = {
                      "error" : self.error,
                      "id" : self.id
                      }
            if self.jsonrpc == "2.0":
                params["jsonrpc"] = self.jsonrpc
            self.response.out.write(dumps(params))
            return
        
        if self.id is None:
            if self.jsonrpc == "2.0":
                self.response.set_status(204) #204 means "No content"
                #self.response.out.write(None)
                return
        
        params = {
                  "jsonrpc" : self.jsonrpc,
                  "result" : self.result,
                  "id" : self.id
                  }
        if isinstance(self.result, dict):
            params.update(self.result)
        cached_content = CachedContent(self.request.path, params)
        cached_content.dump()
        cached_content.write(self.requestHandler)
