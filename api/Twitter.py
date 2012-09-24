from __future__ import unicode_literals, print_function
from lib.gae.JsonRpcDispatcher import JsonRpcDispatcher
from lib.json.JsonRpcRequest import JsonRpcRequest
from lib.json.JsonRpcResponse import JsonRpcResponse
from lib.TwitterAuth import ImplicitFlow
from credentials import TWITTER_CONSUMER_KEY
from urlparse import urlparse, urlunparse, ParseResult
from logging import debug
from model.TwitterUser import TwitterUser
from model.OdenkiUser import OdenkiUser
from lib.json.JsonRpcError import EntityNotFound, MixedAuthentication
from lib2to3.fixer_util import Call

class Twitter(JsonRpcDispatcher):
    
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
        
        implicit_flow = ImplicitFlow()
        callback_url = self._makeCallbackUrl(jrequest.request.url)
        jresponse.setResultValue("callback_url", callback_url)
        auth_url = implicit_flow.getAuthUrl(TWITTER_CONSUMER_KEY, callback_url)
        jresponse.setResultValue("auth_url", auth_url)

    @staticmethod
    def _makeCallbackUrl(url):
        parsed_url = urlparse(url)
        assert isinstance(parsed_url, ParseResult)
        assert len(parsed_url) == 6
        split_callback_url = (parsed_url[0], parsed_url[1], "/api/Twitter/Callback", None, None, None)
        callback_url = urlunparse(split_callback_url)
        return callback_url

class Callback(JsonRpcDispatcher):
    
    def GET(self, jrequest, jresponse):
        assert isinstance(jrequest, JsonRpcRequest)
        assert isinstance(jresponse, JsonRpcResponse)
        jresponse.setId()
        jresponse.setRedirectTarget("/api/Twitter")
        debug(jrequest.request)
        implicit_flow = ImplicitFlow()
        implicit_flow.setAccessToken(jrequest.request)
        implicit_flow.saveToSession()
        try:
            twitter_user = TwitterUser.loadFromSession(self)
            if twitter_user.twitterId != implicit_flow.twitterId:
                raise MixedAuthentication({"twitter_user.twitterId": twitter_user.twitterId, "implicit_flow.twitterId": implicit_flow.twitterId})
        except EntityNotFound:
            try:
                twitter_user = TwitterUser.getByTwitterId(implicit_flow.twitterId)
            except EntityNotFound:
                twitter_user = TwitterUser()
                twitter_user.twitterId = implicit_flow.twitterId

        assert isinstance(twitter_user, TwitterUser)
        assert twitter_user.twitterId == implicit_flow.twitterId
        twitter_user.screenName = implicit_flow.screenName
        twitter_user.accessToken = implicit_flow.accessToken
        
        if twitter_user.odenkiId is None:
            try:
                odenki_user = OdenkiUser.loadFromSession()
                assert isinstance(odenki_user, OdenkiUser)
                twitter_user.odenkiId = odenki_user.odenkiId
            except EntityNotFound:
                odenki_user = OdenkiUser.getNew()
                assert isinstance(odenki_user, OdenkiUser)
                twitter_user.odenkiId = odenki_user.odenkiId
        else:
            try:
                odenki_user = OdenkiUser.loadFromSession()
                if twitter_user.odenkiId != odenki_user.odenkiId:
                    raise MixedAuthentication({"twitter_user.odenkiId": twitter_user.odenkiId, "odenki_user.odenkiId": odenki_user.odenkiId}) 
            except EntityNotFound:
                odenki_user = OdenkiUser.getByOdenkiId(twitter_user.odenkiId)
                odenki_user.saveToSession()
                
        assert twitter_user.odenkiId == odenki_user.odenkiId
        twitter_user.put()
        twitter_user.saveToSession()
        
if __name__ == "__main__":
    mapping = []
    mapping.append(("/api/Twitter/Callback", Callback))
    mapping.append(("/api/Twitter", Twitter))
    from lib.gae import run_wsgi_app
    run_wsgi_app(mapping)
