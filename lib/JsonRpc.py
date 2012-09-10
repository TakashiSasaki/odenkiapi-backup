#from google.appengine import runtime
from model.NdbModel import NdbModel
__all__ = ["JsonRpcError", "JsonRpcRequest", "JsonRpcResponse", "JsonRpcDispatcher"]

from encodings.base64_codec import base64_decode
from json import loads
from lib.JsonEncoder import dumps
from google.appengine.ext.webapp import Request, RequestHandler, Response
from StringIO import StringIO
import csv
from logging import debug, error

class JsonRpcError(object):
    PARSE_ERROR = -32700
    INVALID_REQUEST = -32600
    METHOD_NOT_FOUND = -32601
    INVALID_PARAMS = -32602
    INTERNAL_ERROR = -32603
    SERVER_ERROR_RESERVED_MAX = -32000
    SERVER_ERROR_RESERVED_MIN = -32099

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
            debug("extra data %s:%s" % (argument, values))
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

class JsonRpcResponse(dict):
    """Each JSON-RPC method should return JsonRpcResponse object.
    JsonRpcDispatcher sees it and determines actual HTTP response
    without any other assumptions. 
    """
    
    __slots__ = ["_redirectTarget"]
    
    def __init__(self, request_id):
        dict.__init__(self)
        debug("constructor of JsonRpcResponse object")
        self["id"] = request_id
        #self.requestHandler = request_handler
        #self.request = request_handler.request
        #self.response = request_handler.response
        #self.error = {}
        #self.result = None
        #elf.error = None
    
    #def redirect(self, url):
    #    raise DeprecationWarning()
    #    self.requestHandler.redirect(url)
    #    assert self.response.status == 302
    #    self.setHttpStatus(self.response.status)
    
    def getId(self):
        assert isinstance(self , dict)
        return self.get("id")
    
    def setId(self):
        if self.getId(): return
        from time import time
        self["id"] = time()

    #def delError(self):
    #    if self.has_key("error"): del self["error"]

    def setError(self, error_code, error_message=None, error_data=None):
        assert isinstance(error_code, int)
        assert isinstance(self, dict)
        if self.has_key("error"):
            raise RuntimeError("JSON-RPC error is already set.")
        #assert not hasattr(self, "error")
        self["error"] = {
                      "code": error_code,
                      "message": error_message,
                      "data":error_data
                      }
        if self.getResult(): 
            self.setErrorData(self.getResult())
            self.delResult()
        #http_status = _getHttpStatusFromJsonRpcerror(error_code)
        #self.setHttpStatus(http_status)
        
    def getError(self):
        return self.get("error")

    def setErrorData(self, error_data):
        assert isinstance(error_data, list) or isinstance(error_data, dict)
        assert self.has_key("error")
        assert not self["error"]["data"]
        self["error"]["data"] = error_data
    
    def getErrorData(self):
        if not self.has_key("error"): return None
        return self["error"]["data"]
        
    def setResultValue(self, key, value):
        if self.getError(): 
            raise RuntimeError("JSON-RPC error is already set and any result can't exist simultaneously.")
        if self.get("result") is None: self["result"] = {}
        if not isinstance(self.get("result"), dict):
            raise RuntimeError("Existing JSON-RPC result object is not a dict.")
        if self["result"].get(key):
            raise RuntimeError("Existing JSON-RPC result already has key %s" % key)
        self["result"][key] = value
        return self["result"]
    
    def getResult(self):
        return self.get("result")
        
    def appendResultValue(self, key, value):
        if self.result.has_key(key):
            if not isinstance(self.result.get(key), list):
                self.result[key] = [self.result[key]]
        assert isinstance(self.result.get(key), list)
        self.result["key"].append(value)

    def getExtra(self):
        return self.get("extra")

    def setExtraDict(self, extra_dict):
        assert isinstance(extra_dict, dict)
        if self.get("extra") is not None: raise RuntimeError("JSON-RPC response already has extra object")
        self["extra"] = extra_dict
    
    def setExtraValue(self, k, v):
        extra = self.getExtra()
        if extra is None: self.setExtraDict({})
        extra = self.getExtra()
        assert isinstance(extra, dict)
        if extra.has_key(k): raise RuntimeError("extra dict already has %s key" % k)
        self["extra"][k] = v
        
    def setResult(self, result):
        if self.has_key("result"): raise RuntimeError("result is already set")
        self["result"] = result
        
    def delResult(self):
        if self.has_key("result"): del self["result"]
        
    def updateResult(self, result):
        assert isinstance(self.result, dict)
        self.result.update(result)
        
    def addResult(self, item_to_append_to_result):
        result = self.getResult()
        if result is not None and not isinstance(result, list): return
        if result is None: 
            result = []
            self.setResult(result)
        assert isinstance(result, list)
        result.append(item_to_append_to_result)
        
        
    #def getParam(self, key):
    #    if hasattr(self, "params"):
    #       if isinstance(self.params, dict):
    #           return self.params.get(key)
    #    return self.jsonRequest.get(key)
    
    #def getParams(self):
    #    assert isinstance(self.params, dict)
    #   return self.params
    
    #def getMethod(self):
    #    if not hasattr(self, "method"): return None
    #   assert isinstance(self.method, str) or isinstance(self.method, unicode)
    #    return self.method
    
    #def getRequest(self):
    #   return self.jsonRequest
    
    #def getId(self):
    #    assert isinstance(self.id, None) or isinstance(self.id, int) or isinstance(self.id, long) or isinstance(self.id, str)
    #    return self.id
    
    #def getVersion(self):
    #    if hasattr(self, "jsonrpc"):
    #        if self.jsonrpc == "2.0":
    #            return 2
    #        else: return 1
    #    return None
        
    def getErrorCode(self):
        error_code = self["error"]["code"]
        if isinstance(error_code, int):
            return error_code

    def getFieldNames(self):
        """fieldnames in extra member is non-standard as JSON-RPC but convenient for CSV or TSV output"""
        extra = self.getExtra()
        if not isinstance(extra, dict): return None
        fieldnames = extra.get("fieldnames")
        if not isinstance(fieldnames, list): return None
        return fieldnames
    
    def setFieldNames(self, field_names):
        """fieldnames in extra member is non-standard as JSON-RPC but convenient for CSV or TSV output"""
        self.setExtraValue("fieldnames", field_names)
        
    def setRedirectTarget(self, target_url):
        assert isinstance(target_url, str)
        assert not hasattr(self, "_redirectTarget") 
        self._redirectTarget = target_url
        
    def getRedirectTarget(self):
        if hasattr(self, "_redirectTarget"): return self._redirectTarget

class JsonRpcDispatcher(RequestHandler):
    """JsonRpcDispatcher invokes corresponding methods according to given method parameter"""
    __slot__ = ["methodList", "jsonRpc"]
    
    def __init__(self, request, response):
        RequestHandler.__init__(self, request, response)
        self._initMethodList()

    def _initMethodList(self):
        """ It registers user methods to self.methodList.
        User methods are expected to take just one JSON-RPC object.  
        """
        self.methodList = {}
        self.methodList.update(self.__class__.__dict__)
        assert isinstance(self.methodList, dict)
        
        def d(key):
            try:
                del self.methodList[key]
            except KeyError:
                pass

        d("__slot__")
        d("__module__")
        d("__main__")
        d("__dict__")
        d("__weakref__")
        d("__doc__")
        d("__init__")
        d("get")
        d("post")
        d("put")
        d("head")
        d("options")
        d("delete")
        d("trace")
        d("_write")
        d("_invokeMethod")
        d("_initMethodList")
        
        for k, v in self.methodList.iteritems():
            if isinstance(k, str):
                self.methodList[k.decode()] = v
    
    def _invokeMethod(self, method_name, json_rpc_request):
        assert isinstance(json_rpc_request, JsonRpcRequest)
        json_rpc_response = JsonRpcResponse(json_rpc_request.getId())
        x = self.methodList[method_name](self, json_rpc_request, json_rpc_response)
        assert x is None
        return json_rpc_response
    
    def get(self, *args):
        jrequest = JsonRpcRequest(self.request)
        jresponse = self._invokeMethod(jrequest.method, jrequest)
        self._write(jresponse)

    def post(self, *args):
        json_rpc_request = JsonRpcRequest(self.request)
        json_rpc_response = self._invokeMethod(json_rpc_request.method, json_rpc_request)
        self._write(json_rpc_response)
    
    def put(self, *args):
        json_rpc_request = JsonRpcRequest(self.request)
        json_rpc_response = self._invokeMethod(json_rpc_request.method, json_rpc_request)
        self._write(json_rpc_response)
    
    def head(self, *args):
        json_rpc_request = JsonRpcRequest(self.request)
        json_rpc_response = self._invokeMethod(json_rpc_request.method, json_rpc_request)
        self._write(json_rpc_response)
    
    def options(self, *args):
        json_rpc_request = JsonRpcRequest(self.request)
        json_rpc_response = self._invokeMethod(json_rpc_request.method, json_rpc_request)
        self._write(json_rpc_response)
        
    def delete(self, *args):
        json_rpc_request = JsonRpcRequest(self.request)
        json_rpc_response = self._invokeMethod(json_rpc_request.method, json_rpc_request)
        self._write(json_rpc_response)
        
    def trace(self, *args):
        json_rpc_request = JsonRpcRequest(self.request)
        json_rpc_response = self._invokeMethod(json_rpc_request.method, json_rpc_request)
        self._write(json_rpc_response)

    def _write(self, json_rpc_response):
        """write JSON-RPC response as it is"""
        assert isinstance(json_rpc_response, JsonRpcResponse)
        assert isinstance(json_rpc_response, dict)
        
        if json_rpc_response.getRedirectTarget():
            assert isinstance(self.response, Response)
            self.redirect(json_rpc_response.getRedirectTarget())
            debug("redirecting to %s" % json_rpc_response.getRedirectTarget())
            return
        
        # notification has no id
        if json_rpc_response.getId() is None:
            debug("JSON-RPC notification")
            if not json_rpc_response.has_key("error") and not json_rpc_response.has_key("result"):
                # http://www.simple-is-better.org/json-rpc/jsonrpc20-over-http.html
                self.response.set_status(204) # No content
                self.response.content_type = "text/plain"
                return
            json_rpc_response.setError(JsonRpcError.INVALID_REQUEST, "Response for notification should have neither result nor error.")

        if json_rpc_response.has_key("error"):
            debug("JSON RPC response with error.")
            assert  json_rpc_response.getResult() is None
            self.response.content_type = "application/json"
            self.response.status = JsonRpcDispatcher._getHttpStatusFromJsonRpcError(json_rpc_response.getErrorCode()) 
            self.response.out.write(dumps(json_rpc_response))
            return
        
        # HTTP response in given format
        if self.request.get("format") == "tsv":
            self._writeTsv(json_rpc_response)
            return
        if self.request.get("format") == "csv":
            self._writeCsv(json_rpc_response)
            return
        if self.request.get("callback"):
            self._writeJsonP(json_rpc_response)
            return
        self._writeJson(json_rpc_response)
    
    def _writeJson(self, json_rpc_response):
        assert isinstance(json_rpc_response, JsonRpcResponse)
        assert isinstance(json_rpc_response, dict)
        self.response.content_type = "application/json"
        self.response.out.write(dumps(json_rpc_response))
        return
    
    def _writeCsv(self, json_rpc_response, dialect=csv.excel, content_type="text/csv"):
        assert isinstance(json_rpc_response, JsonRpcResponse)
        output = StringIO()
        csv_writer = csv.writer(output, dialect)
        fieldnames = json_rpc_response.getFieldNames()
        if isinstance(fieldnames, list):
            csv_writer.writerow(fieldnames)
        result = json_rpc_response.getResult()
        if not isinstance(result, list): result = []
        for record in result:
            if isinstance(record, list):
                csv_writer.writerow(record)
                continue
            if isinstance(record, NdbModel):
                csv_writer.writerow(record.to_list())
                continue
            error("result contains neither list nor NdbModel")
        self.response.out.write(output.getvalue())
        self.response.content_type = content_type
    
    def _writeTsv(self, json_rpc_response):
        self._writeCsv(json_rpc_response, dialect=csv.excel_tab, content_type="application/vnd.ms-excel")
        
    def _writeJsonP(self, json_rpc_response):
        result = json_rpc_response.getResult()
        if not isinstance(result, dict) or not isinstance(result, list):
            raise RuntimeError("result is neither dict or list")
        self.response.out.write(dumps(result))
        self.response.content_type = "application/javascript"

    @classmethod
    def _getHttpStatusFromJsonRpcError(cls, json_rpc_error):
        if json_rpc_error == JsonRpcError.PARSE_ERROR:
            return 500
        if json_rpc_error == JsonRpcError.INVALID_REQUEST:
            return 400
        if json_rpc_error == JsonRpcError.METHOD_NOT_FOUND:
            return 404
        if json_rpc_error == JsonRpcError.INVALID_PARAMS:
            return 500
        if json_rpc_error == JsonRpcError.INTERNAL_ERROR:
            return 500
        if json_rpc_error >= JsonRpcError.SERVER_ERROR_RESERVED_MIN and json_rpc_error <= JsonRpcError.SERVER_ERROR_RESERVED_MAX:
            return 500
        return None
    
    def doesAcceptHtml(self, jrequest, jresponse):
        if self.request.accept.accept_html(): return True
        self.response.setHttpStatus(406)
        assert isinstance(jresponse, JsonRpcResponse)
        error_message = "user agent does not accept text/html response"
        jresponse.setError(JsonRpcError.INVALID_REQUEST, error_message)
