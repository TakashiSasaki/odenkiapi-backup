from __future__ import unicode_literals, print_function
from lib.gae.JsonRpcDispatcher import JsonRpcDispatcher
from lib.json.JsonRpcRequest import JsonRpcRequest
from lib.json.JsonRpcResponse import JsonRpcResponse
from credentials import TWITTER_CONSUMER_KEY
from logging import debug
from model.TwitterUser import TwitterUser
from model.OdenkiUser import OdenkiUser
from lib.json.JsonRpcError import EntityNotFound, MixedAuthentication

class Twitter2(JsonRpcDispatcher):
    
    def GET(self, jrequest, jresponse):
        assert isinstance(jrequest, JsonRpcRequest)
        assert isinstance(jresponse, JsonRpcResponse)
        jresponse.setId()
        try:
            twitter_user = TwitterUser.loadFromSession()
            assert isinstance(twitter_user, TwitterUser)
            jresponse.setResultValue("twitterId", twitter_user.twitterId)
            jresponse.setResultValue("screenName", twitter_user.screenName)
            jresponse.setResultValue("odenkiId", twitter_user.odenkiId)
        except EntityNotFound: pass
        
class Callback(JsonRpcDispatcher):
    
    def GET(self, jrequest, jresponse):
        assert isinstance(jrequest, JsonRpcRequest)
        assert isinstance(jresponse, JsonRpcResponse)
        jresponse.setId()
        jresponse.setRedirectTarget("/api/Twitter2")
        
if __name__ == "__main__":
    mapping = []
    mapping.append(("/api/Twitter2/Callback", Callback))
    mapping.append(("/api/Twitter2", Twitter2))
    from lib.gae import run_wsgi_app
    run_wsgi_app(mapping)
