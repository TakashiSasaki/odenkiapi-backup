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

def _toHttpStatus(error_code):
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

def _getJsonFromUrl(params):
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
        params_string = base64_decode(base64_params)
        json_from_url["params"] = loads(params_string)
    return json_from_url
        
def _getJsonFromBody(body):
    assert isinstance(body, str)
    json_from_body = loads(body)
    if json_from_body is None:
        json_from_body = {}
    assert isinstance(json_from_body, dict)
    return json_from_body

class JsonRpc(object):
    __slots__ = [ "request", "response", "jsonRequest", "requestHandler", "jsonrpc", "method", "params", "id", "result", "error", "log", "httpStatus"]
    
    def __init__(self, request_handler):
        self.requestHandler = request_handler
        self.request = request_handler.request
        self.response = request_handler.response
        #self.error = {}
        self._getJsonRequest()
        if self.jsonRequest:
            self.jsonrpc = self.jsonRequest.get("jsonrpc")
            if  self.jsonRequest.has_key("method"):
                self.method = self.jsonRequest.get("method")
            self.params = self.jsonRequest.get("params")
            self.id = self.jsonRequest.get("id")
            if isinstance(self.id, list) and len(self.id) == 1:
                self.id = self.id[0]
        
    def _getArgumentDict(self):
        d = {}
        for a in self.request.arguments():
            assert isinstance(a, unicode)
            d[a] = self.request.get_all(a)
            if isinstance(d[a], list) and len(d[a]) == 1:
                d[a] = d[a][0]
        return d

    def redirect(self, url):
        self.requestHandler.redirect(url)
        assert self.response.status == 302
        self.setHttpStatus(self.response.status)

    def setHttpStatus(self, http_status):
        assert isinstance(http_status, int)
        assert not hasattr(self, "httpStatus")
        self.httpStatus = http_status
        
    def setError(self, error_code, error_message=None, error_data=None):
        assert isinstance(error_code, int)
        assert not hasattr(self, "error")
        self.error = {
                      "code": error_code,
                      "message": error_message,
                      "data":error_data
                      }
        http_status = _toHttpStatus(error_code)
        self.setHttpStatus(http_status)
        
    def setResultValule(self, key, value):
        if not hasattr(self, "result"):
            self.result = {}
        assert isinstance(self.result, dict)
        assert not self.result.has_key(key)
        self.result[key] = value
        
    def appendResultValue(self, key, value):
        assert isinstance(self.result.has_key("key"), list)
        self.result["key"].append(value)
        
    def addLog(self, log_message):
        if not hasattr(self, "log"):
            self.log = []
        self.log.append(log_message)

    def setResult(self, result):
        assert not hasattr(self, "result") or self.result is None
        self.result = result
        
    def updateResult(self, result):
        assert isinstance(self.result, dict)
        self.result.update(result)
        
    def getParam(self, key):
        if hasattr(self, "params"):
            if isinstance(self.params, dict):
                return self.params.get(key)
        return self.jsonRequest.get(key)
    
    def getParams(self):
        assert isinstance(self.params, dict)
        return self.params
    
    def getMethod(self):
        if not hasattr(self, "method"): return None
        assert isinstance(self.method, str) or isinstance(self.method, unicode)
        return self.method
    
    def getRequest(self):
        return self.jsonRequest
    
    def getId(self):
        assert isinstance(self.id, None) or isinstance(self.id, int) or isinstance(self.id, long) or isinstance(self.id, str)
        return self.id
    
    def getVersion(self):
        if hasattr(self, "jsonrpc"):
            if self.jsonrpc == "2.0":
                return 2
            else: return 1
        return None
        
    def getErrorCode(self):
        try:
            error_code = self.error["code"]
            if isinstance(error_code, int):
                return error_code
        except:
            pass
        return None
    
    def _getJsonRequest(self):
        """getJsonRequest is intended to gather as many parameters as possible 
        even if parameters in URL or request body does not meet JSON-RPC 2.0 specification.
        """
        if self.request.method == "POST" or self.request.method == "PUT":
            # POST can change the state of servers.
            # PUT should be idempotent.
            try:
                self.jsonRequest = _getJsonFromBody(self.request.body)
                return
            except JSONDecodeError, e:
                self.jsonRequest = None
                self.setError(JSON_RPC_ERROR_PARSE_ERROR, e.message)
                return
        if self.request.method == "GET" or self.request.method == "DELETE":
            # GET should not change the state of servers.
            # DELETE should be idempotent.
            try:
                argument_dict = self._getArgumentDict()
                self.jsonRequest = _getJsonFromUrl(argument_dict)
                assert isinstance(self.jsonRequest, dict)
                return
            except JSONDecodeError, e:
                self.jsonRequest = None
                self.setError(JSON_RPC_ERROR_PARSE_ERROR, e.message)
                return

        self.jsonRequest = None
        self.setError(JSON_RPC_ERROR_INVALID_REQUEST, "%s is unknown HTTP method" % self.request.method)
        
    def write(self):
        if hasattr(self, "error"):
            assert isinstance(self.error, dict)
            assert not hasattr(self, "result")
            self.response.content_type = "application/json"
            params = {
                      "error" : self.error,
                      }
            if hasattr(self, "id"):
                params["id"] = self.id
            if hasattr(self, "log"):
                params["log"] = self.log
            if hasattr(self, "jsonrpc") and self.jsonrpc == "2.0":
                params["jsonrpc"] = self.jsonrpc
            self.response.out.write(dumps(params))
            return
        
        # notification has no id
        if not hasattr(self, "id") and hasattr(self, "method"):
            assert not hasattr(self, "error")
            assert not hasattr(self, "result")
            assert not hasattr(self, "httpStatus")
            self.response.set_status(204) # No content
            return
        
        if hasattr(self, "id") and hasattr(self, "method"):
            params = {
                      "id" : self.id
                      }
            if hasattr(self, "result"):
                params["result"] = self.result
            if hasattr(self, "log"):
                params["log"] = self.log
            if self.jsonrpc == "2.0":
                params["jsonrpc"] = self.jsonrpc
            cached_content = CachedContent(self.request.path, params)
            cached_content.dump()
            if hasattr(self, "httpStatus"):
                self.response.set_status(self.httpStatus)
            cached_content.write(self.requestHandler)
            return
            
        if hasattr(self, "log"):
            self.result["log"] = self.log
        cached_content = CachedContent(self.request.path, self.result)
        cached_content.dump()
        cached_content.write(self.requestHandler)
