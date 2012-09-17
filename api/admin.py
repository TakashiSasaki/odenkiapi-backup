from __future__ import unicode_literals, print_function
from lib.gae import JsonRpcDispatcher
from lib.json.JsonRpcRequest import JsonRpcRequest
from lib.json.JsonRpcResponse import JsonRpcResponse
from logging import debug
from google.appengine.api import users

class AdminMode(JsonRpcDispatcher):
    
    def GET(self, jrequest, jresponse):
        assert isinstance(jrequest, JsonRpcRequest)
        assert isinstance(jresponse, JsonRpcResponse)
        jresponse.setId()
        jresponse.setResult({"mode": "enabled"})
        #debug(users)
        #debug(dir(users))
        
    def slidecreate(self, jrequest, jresponse):
        assert isinstance(jrequest, JsonRpcRequest)
        assert isinstance(jresponse, JsonRpcResponse)
        jresponse.setId()
    
if __name__ == "__main__":
    mapping = []
    mapping.append(("/api/admin/mode", AdminMode))
    from lib.gae import run_wsgi_app
    run_wsgi_app(mapping)
