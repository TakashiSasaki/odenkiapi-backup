from __future__ import unicode_literals, print_function
from lib.gae.JsonRpcDispatcher import JsonRpcDispatcher
from lib.json.JsonRpcRequest import JsonRpcRequest
from lib.json.JsonRpcResponse import JsonRpcResponse
import gaesessions
from lib.TwitterAuth import ImplicitFlow
from credentials import TWITTER_CONSUMER_KEY
from urlparse import urlparse,urlunparse,ParseResult

class Twitter(JsonRpcDispatcher):
    
    def GET(self, jrequest, jresponse):
        assert isinstance(jrequest, JsonRpcRequest)
        assert isinstance(jresponse, JsonRpcResponse)
        jresponse.setId()
        
    def login(self, jrequest, jresponse):
        assert isinstance(jrequest, JsonRpcRequest)
        assert isinstance(jresponse, JsonRpcResponse)
        jresponse.setId()
        jresponse.setResultValue("url", jrequest.url)
        parsed_url = urlparse(jrequest.url)
        assert isinstance(parsed_url,ParseResult)
        assert len(parsed_url)==6
        split_callback_url = (parsed_url[0],parsed_url[1],"/api/Twitter/Callback",None,None,None)
        callback_url = urlunparse(split_callback_url)
        jresponse.setResultValue("callback_url", callback_url)
        implicit_flow = ImplicitFlow(TWITTER_CONSUMER_KEY, callback_url)
        jresponse.setResultValue("authUrl", implicit_flow.authUrl)
        jresponse.setRedirectTarget(implicit_flow.authUrl)

class Callback(JsonRpcDispatcher):
    
    def GET(self, jrequest, jresponse):
        assert isinstance(jrequest, JsonRpcRequest)
        assert isinstance(jresponse, JsonRpcResponse)
        jresponse.setId()

if __name__== "__main__":
    mapping = []
    mapping.append(("/api/Twitter/Callback", Twitter))
    mapping.append(("/api/Twitter", Twitter))
    from lib.gae import run_wsgi_app
    run_wsgi_app(mapping)
