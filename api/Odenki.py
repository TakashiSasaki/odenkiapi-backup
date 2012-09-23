from __future__ import unicode_literals, print_function
from lib.gae.JsonRpcDispatcher import JsonRpcDispatcher
from lib.json.JsonRpcRequest import JsonRpcRequest
from lib.json.JsonRpcResponse import JsonRpcResponse
from model.OdenkiUser import OdenkiUser

class Odenki(JsonRpcDispatcher):
    
    def GET(self, jrequest, jresponse):
        assert isinstance(jrequest, JsonRpcRequest)
        assert isinstance(jresponse, JsonRpcResponse)
        jresponse.setId()
        odenki_user = OdenkiUser.loadFromSession()
        assert isinstance(odenki_user, OdenkiUser)
        jresponse.setResultValue("odenkiId", odenki_user.odenkiId)
        jresponse.setResultValue("odenkiName", odenki_user.odenkiName)
        
if __name__ == "__main__":
    mapping = []
    mapping.append(("/api/Odenki", Odenki))
    from lib.gae import run_wsgi_app
    run_wsgi_app(mapping)