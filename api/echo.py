#from google.appengine.ext.webapp import RequestHandler
from lib.JsonRpc import *
#import logging
#logger = logging.getLogger()
#logger.setLevel(logging.DEBUG)
#logger.debug("Echo.py was loaded")
import lib

class Echo(JsonRpcDispatcher):
    """Echo returns given RPC object as it is."""
    
    def GET(self, json_rpc_request):
        assert isinstance(json_rpc_request, JsonRpcRequest)
        return self.echo(json_rpc_request)
        
    def TRACE(self, json_rpc_request):
        assert isinstance(json_rpc_request, JsonRpcRequest)
        return self.echo(json_rpc_request)

    def echo(self, json_rpc_request):
        assert isinstance(json_rpc_request, JsonRpcRequest)
        lib.debug("entered in Echo.echo")
        json_rpc_response = JsonRpcResponse(json_rpc_request.id)
        json_rpc_response.result = {
                                    "id": json_rpc_request.id,
                                    "params" : json_rpc_request.params,
                                    "extras" :json_rpc_request.extras,
                                    "jsonrpc" : json_rpc_request.jsonrpc
                                    }
        return json_rpc_response
    
from lib import runWsgiApp
if __name__ == "__main__":
    runWsgiApp(Echo, "/api/echo")
