from google.appengine.ext.webapp import RequestHandler
from lib.JsonRpc import *
from simplejson import dumps
import lib

def _getHttpStatusFromJsonRpcerror(json_rpc_error):
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

class JsonRpcDispatcher(RequestHandler):
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
                lib.debug("key = " + k + " value = " + str(v))
                self.methodList[k.decode()] = v
    
    def _invokeMethod(self, method_name, json_rpc_request):
        lib.debug("_invokeMethod invokes %s" % method_name)
        return self.methodList[method_name](self, json_rpc_request)
        
    def get(self):
        json_rpc_request = JsonRpcRequest(self.request)
        json_rpc_response = self._invokeMethod(json_rpc_request.method, json_rpc_request)
        lib.debug("_invokeMethod returns %s" % type(json_rpc_response))
        assert isinstance(json_rpc_response, JsonRpcResponse)
        self._write(json_rpc_response)

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
        assert isinstance(json_rpc_response, JsonRpcResponse)
        if json_rpc_response.error:
            assert  json_rpc_response.result is None
            self.response.content_type = "application/json"
            response_dict = {
                      "error" : json_rpc_response.error,
                      }
            if hasattr(json_rpc_response, "id"):
                response_dict["id"] = json_rpc_response.id
            if hasattr(json_rpc_response, "log"):
                response_dict["log"] = json_rpc_response.log
            if hasattr(json_rpc_response, "jsonrpc"):
                response_dict["jsonrpc"] = json_rpc_response.jsonrpc
            if hasattr(json_rpc_response, "extras"):
                response_dict["extras"] = json_rpc_response.extras
            self.response.status = _getHttpStatusFromJsonRpcerror(json_rpc_response.error.code) 
            self.response.out.write(dumps(response_dict))
            return
        
        # notification has no id
        if not hasattr(json_rpc_response, "id"):
            assert json_rpc_response.error is None
            assert json_rpc_response.result is None
            assert not hasattr(self, "result")
            self.response.set_status(204) # No content
            return
        
        lib.debug("json_rpc_response has result")
        response_dict = {
                      "id" : json_rpc_response.id
                      }
        if hasattr(json_rpc_response, "result"):
            response_dict["result"] = json_rpc_response.result
        if hasattr(json_rpc_response, "log"):
            response_dict["log"] = json_rpc_response.log
        if hasattr(json_rpc_response, "jsonrpc"):
            response_dict["jsonrpc"] = json_rpc_response.jsonrpc
        if hasattr(json_rpc_response, "extras"):
            response_dict["extras"] = json_rpc_response.extras
        self.response.out.write(dumps(response_dict))
        return
