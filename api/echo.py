from lib.RequestDispatcher import RequestDispatcher
from google.appengine.ext.webapp import RequestHandler
#import logging
#logger = logging.getLogger()
#logger.setLevel(logging.DEBUG)
#logger.debug("Echo.py was loaded")
import lib

#class Echo(RequestDispatcher):
class Echo(RequestHandler):
    """Echo returns given RPC object as it is."""
    #def __init__(self):
    #    RequestDispatcher.__init__(self)
    
    def echo(self, rpc):
        rpc.result = rpc.getRequest()
    
    def post(self):
        self.response.out.write("echo")
        #self.get()
        
    def get(self):
        self.response.out.write("echo")
        

from lib import runWsgiApp
if __name__ == "__main__":
    lib.debug("abc")
    runWsgiApp(Echo, "/api/echo")
