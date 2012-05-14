from google.appengine.ext.webapp import RequestHandler
import lib.JsonRpc
from lib.debug import *

class MethodsHandler(RequestHandler):
    __slot__ = ["methodList", "jsonRpc"]
    
    def _initMethodList(self):
        RequestHandler.__init__(self)
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
        d("put")
        d("delete")
        d("post")
        d("head")
        d("_invokeMethod")
        d("_initMethodList")
        
        for k, v in self.methodList.iteritems():
            if isinstance(k, str):
                debug("key = " + k + " value = " + str(v))
                self.methodList[k.decode()] = v
    
    def _invokeMethod(self, method_name, json_rpc):
        self.methodList[method_name](self, json_rpc)
        
    def get(self):
        self._initMethodList()
        
        json_rpc = lib.JsonRpc.JsonRpc(self)
        if json_rpc.getErrorCode():
            json_rpc.write()
            return
        
        method = json_rpc.getMethod()
        if method is None:
            method = "default"
        
        self._invokeMethod(method, json_rpc)
        json_rpc.write()
        return
