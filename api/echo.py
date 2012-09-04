from lib.RequestDispatcher import RequestDispatcher
from google.appengine.ext.webapp import RequestHandler
from lib.JsonRpc import *
#import logging
#logger = logging.getLogger()
#logger.setLevel(logging.DEBUG)
#logger.debug("Echo.py was loaded")
import lib

class Echo(RequestDispatcher):
    """Echo returns given RPC object as it is."""
    
    def echo(self, json_rpc_request):
        lib.debug("entered in Echo.echo")
        json_rpc_response = JsonRpcResponse(json_rpc_request.id)
        json_rpc_response.result = {
                                    "id": json_rpc_request.id,
                                    "params" : json_rpc_request.params,
                                    "extras" :json_rpc_request.extras,
                                    "jsonrpc" : json_rpc_request.jsonrpc
                                    }
        return json_rpc_response
    
    #def get(self):
    #    self.response.out.write(self.request.get_all("abc"))

from lib import runWsgiApp
if __name__ == "__main__":
    lib.debug("abc")
    runWsgiApp(Echo, "/api/echo")
