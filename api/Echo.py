from google.appengine.ext.webapp import RequestHandler
from lib.JsonRpc import JsonRpc
from lib.debug import *

class Echo(RequestHandler):
    
    __slot__ = ["jsonRpc"]
    
    def get(self):
        self.jsonRpc = JsonRpc(self)
        self.jsonRpc.result = self.jsonRpc.getRequest()
        self.jsonRpc.write()
        return
    
    def post(self):
        self.get()

from lib import runWsgiApp
if __name__ == "__main__":
    runWsgiApp(Echo, "/api/Echo")
