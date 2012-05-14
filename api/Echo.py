from lib.MethodsHandler import MethodsHandler
from lib.debug import *

class Echo(MethodsHandler):
    def __init__(self):
        MethodsHandler.__init__(self)
    
    def echo(self, rpc):
        rpc.result = rpc.getRequest()
    
    def post(self):
        self.get()

from lib import runWsgiApp
if __name__ == "__main__":
    runWsgiApp(Echo, "/api/Echo")
