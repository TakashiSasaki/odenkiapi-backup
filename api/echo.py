#from google.appengine.ext.webapp import RequestHandler
from lib.JsonRpc import *
#import logging
#logger = logging.getLogger()
#logger.setLevel(logging.DEBUG)
#logger.debug("Echo.py was loaded")
from logging import debug

class Echo(JsonRpcDispatcher):
    """Echo returns given RPC object as it is."""
    
    def GET(self, json_rpc_request):
        debug("entered in Echo.GET")
        assert isinstance(json_rpc_request, JsonRpcRequest)
        return self.echo(json_rpc_request)
        
    def TRACE(self, json_rpc_request):
        debug("entered in Echo.TRACE")
        assert isinstance(json_rpc_request, JsonRpcRequest)
        return self.echo(json_rpc_request)

    def echo(self, json_rpc_request):
        assert isinstance(json_rpc_request, JsonRpcRequest)
        if json_rpc_request.getId() is None:
            json_rpc_response = JsonRpcResponse(None)
            json_rpc_response.setError(JsonRpcError.INVALID_PARAMS, "id is mandatory")
            return json_rpc_response

        debug("entered in Echo.echo with id = %s " % json_rpc_request.getId())
        json_rpc_response = JsonRpcResponse(json_rpc_request.getId())
        json_rpc_response.setResult({
                                    "id": json_rpc_request.getId(),
                                    "params" : json_rpc_request.getParams(),
                                    "extra" :json_rpc_request.getExtra(),
                                    "jsonrpc" : json_rpc_request.getJsonRpcVersion()
                                    })
        return json_rpc_response
    
if __name__ == "__main__":
    from google.appengine.ext.webapp import WSGIApplication
    application = WSGIApplication([("/api/echo", Echo)], debug=True)
    from google.appengine.ext.webapp.util import run_wsgi_app
    run_wsgi_app(application)
