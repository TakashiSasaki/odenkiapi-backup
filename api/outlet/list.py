from __future__ import unicode_literals, print_function
from lib.gae.JsonRpcDispatcher import JsonRpcDispatcher
from lib.json.JsonRpcRequest import JsonRpcRequest
from lib.json.JsonRpcResponse import JsonRpcResponse
from model.Outlet import Outlet
from lib.json.JsonRpcError import EntityNotFound
from lib.gae import run_wsgi_app

class _Outlet(JsonRpcDispatcher):

    def GET(self, jrequest, jresponse):
        assert isinstance(jrequest, JsonRpcRequest)
        assert isinstance(jresponse, JsonRpcResponse)
        jresponse.setId()
        for outlet in Outlet.query():
            jresponse.addResult(outlet)

if __name__ == "__main__":
    mapping = []
    mapping.append(("/api/outlet/list", _Outlet))
    run_wsgi_app(mapping)
