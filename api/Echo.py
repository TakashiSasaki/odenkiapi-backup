from lib.RequestDispatcher import RequestDispatcher

class Echo(RequestDispatcher):
    """Echo returns given RPC object as it is."""
    def __init__(self):
        RequestDispatcher.__init__(self)
    
    def echo(self, rpc):
        rpc.result = rpc.getRequest()
    
    def post(self):
        self.get()

from lib import runWsgiApp
if __name__ == "__main__":
    runWsgiApp(Echo, "/api/Echo")
