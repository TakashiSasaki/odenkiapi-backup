from __future__ import unicode_literals, print_function
from lib.gae import JsonRpcDispatcher
from lib.json.JsonRpcRequest import JsonRpcRequest
from lib.json.JsonRpcResponse import JsonRpcResponse
from logging import debug
from google.appengine.api import users
from model.AdminUser import AdminUser

class AdminMode(JsonRpcDispatcher):
    
    def GET(self, jrequest, jresponse):
        assert isinstance(jrequest, JsonRpcRequest)
        assert isinstance(jresponse, JsonRpcResponse)
        jresponse.setId()
        jresponse.setResult({"mode": "enabled"})
        user = users.get_current_user()
        jresponse.setResultValue("login_url", users.create_login_url("/api/admin/mode"))
        jresponse.setResultValue("logout_url", users.create_logout_url("/api/admin/mode"))
        debug(AdminUser.fetchAdminUsers())
        if user:
            jresponse.setResultValue("user_id", user.user_id())
            jresponse.setResultValue("email", user.email())
            jresponse.setResultValue("nickname", user.nickname())
        else:
            jresponse.setResultValue("user_id", None)
            jresponse.setResultValue("email", None)
            jresponse.setResultValue("nickname", None)
        jresponse.setResultValue("adminUsers", AdminUser.fetchAdminUsers())
        
    def slidecreate(self, jrequest, jresponse):
        assert isinstance(jrequest, JsonRpcRequest)
        assert isinstance(jresponse, JsonRpcResponse)
        jresponse.setId()
        self.GET(jrequest, jresponse)

    def changed(self, jrequest, jresponse):
        assert isinstance(jrequest, JsonRpcRequest)
        assert isinstance(jresponse, JsonRpcResponse)
        jresponse.setId()
                
    
if __name__ == "__main__":
    mapping = []
    mapping.append(("/api/admin/mode", AdminMode))
    from lib.gae import run_wsgi_app
    run_wsgi_app(mapping)
