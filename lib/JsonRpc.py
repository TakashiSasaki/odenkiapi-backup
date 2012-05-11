from encodings.base64_codec import base64_decode
from simplejson import dumps, load, loads, JSONDecodeError
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


from lib.CachedContent import CachedContent
class JsonRpc(object):
    __slots__ = [ "request", "response", "jsonRequest", "requestHandler", "request", "response", "jsonrpc", "method", "params", "id", "result", "error"]
    
    def __init__(self, request_handler):
        self.requestHandler = request_handler
        self.request = request_handler.request
        self.response = request_handler.response
        self.error = {}
        self.getJsonRequest()
        if self.jsonRequest:
            self.jsonrpc = self.jsonRequest.get("jsonrpc", None)
            self.method = self.jsonRequest.get("method", None)
            self.params = self.jsonRequest.get("params", None)
            self.id = self.jsonRequest.get("id", None)
        self.result = None

    def setErrorCode(self, error_code):
        assert isinstance(error_code, int)
        assert isinstance(self.error, dict)
        self.error["code"] = error_code
    
    def getHttpStatus(self):
        error_code = self.error["code"]
        return toHttpStatus(error_code)
    
    def setErrorMessage(self, error_message):
        assert isinstance(error_message, str)
        self.error["message"] = error_message
    
    def setErrorData(self, error_data):
        self.error["data"] = error_data

    def getJsonRequest(self):
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
                self.jsonRequest = getJsonFromUrl(self.request.url)
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
                      "jsonrpc" : self.jsonrpc,
                      "error" : self.error,
                      "id" : self.id
                      }
            self.response.out.write(dumps(params))
            return
        
        if self.id is None:
            self.response.out.write()
            self.response.set_status(204)
            return
        
        if self.method == "echo" and self.result is None:
            self.result = self.jsonRequest

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
