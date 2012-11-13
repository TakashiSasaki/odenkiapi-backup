from __future__ import unicode_literals, print_function
from warnings import warn
from JsonRpcError import JsonRpcError

class JsonRpcResponse(dict):
    """Each JSON-RPC method should return JsonRpcResponse object.
    JsonRpcDispatcher sees it and determines actual HTTP response
    without any other assumptions. 
    """
    
    __slots__ = ["_redirectTarget", "_columns"]
    
    def __init__(self, request_id):
        dict.__init__(self)
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
    
    def setErrorInvalidParameter(self, e):
        if isinstance(e, Exception):
            error_message = unicode(e)
        elif isinstance(e, unicode) or isinstance(e, str):
            error_message = e
        self.setError(JsonRpcError.INVALID_PARAMS, error_message)
    
    def setError(self, error_code, error_message=None, error_data=None, error_name=None):
        if error_code is None:
            error_code = JsonRpcError.SERVER_ERROR_RESERVED_MIN
        assert isinstance(error_code, int)
        assert isinstance(self, dict)
        if self.has_key("error"):
            raise RuntimeError("JSON-RPC error is already set.")
        #assert not hasattr(self, "error")
        self["error"] = {
                      "code": error_code,
                      "name" : error_name, # this is non standard field
                      "message": error_message,
                      "data":error_data,
                      }
        if self.getResult():  
            self["canceled_result"] = self.getResult()
            self.delResult()
        #http_status = _getHttpStatusFromJsonRpcerror(error_code)
        #self.setHttpStatus(http_status)
        return

    def setErrorData(self, error_data):
        assert isinstance(error_data, list) or isinstance(error_data, dict)
        assert self.has_key("error")
        assert not self["error"]["data"]
        self["error"]["data"] = error_data
    
    def getErrorData(self):
        if not self.has_key("error"): return None
        return self["error"]["data"]
        
    def getError(self):
        self["error"]
    
    def hasError(self):
        if self.has_key("error"): return True
        else: return False

    def setResultValue(self, key, value):
        if self.hasError(): 
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
    
    def getExtraValue(self, k):
        extra = self.getExtra()
        if extra is None: return
        assert isinstance(extra, dict)
        return extra.get(k)
        
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
        warn("getFieldNames is deprecated. Use getColumns instead.", DeprecationWarning)
        """fieldnames in extra member is non-standard as JSON-RPC but convenient for CSV or TSV output"""
        extra = self.getExtra()
        if not isinstance(extra, dict): return None
        fieldnames = extra.get("fieldnames")
        if not isinstance(fieldnames, list): return None
        return fieldnames
    
    def setFieldNames(self, field_names):
        warn("setFieldNames is deprecated. Use setColumns instead.", DeprecationWarning)
        """fieldnames in extra member is non-standard as JSON-RPC but convenient for CSV or TSV output"""
        self.setExtraValue("fieldnames", field_names)
        
    def setColumns(self, columns):
        assert not hasattr(self, "_columns")
        self._columns = columns 
        
    def getColumns(self):
        return getattr(self, "_columns", None)
        
    def setRedirectTarget(self, target_url):
        assert isinstance(target_url, unicode)
        #assert not hasattr(self, "_redirectTarget") 
        self._redirectTarget = target_url
        
    def getRedirectTarget(self):
        if hasattr(self, "_redirectTarget"): return self._redirectTarget

    def hasRedirectTarget(self):
        return True if hasattr(self, "_redirectTarget") else False

    def delRedirectTarget(self):
        del(self._redirectTarget)
