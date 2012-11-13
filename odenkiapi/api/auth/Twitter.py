#!-*- coding:utf-8 -*-
from __future__ import unicode_literals, print_function
from lib.gae.JsonRpcDispatcher import JsonRpcDispatcher
from lib.json.JsonRpcRequest import JsonRpcRequest
from lib.json.JsonRpcResponse import JsonRpcResponse
from credentials import TWITTER_CONSUMER_KEY, TWITTER_CONSUMER_SECRET
from model.TwitterUser import TwitterUser
from lib.json.JsonRpcError import EntityNotFound, OAuthError, InconsistentAuthentiation
import oauth2
from urlparse import parse_qsl
from urllib import urlencode
import gaesessions
from model.OdenkiUser import OdenkiUser
from google.appengine.ext import ndb

"""Twitter OAuth consumer secret and consumer key for odenkiapi
can be obtained at https://dev.twitter.com/apps/1919034/show """

REQUET_TOKEN_URL = "https://api.twitter.com/oauth/request_token"
AUTHORIZE_URL = "https://api.twitter.com/oauth/authorize"
ACCESS_TOKEN_URL = "https://api.twitter.com/oauth/access_token"
#CALLBACK_URL = "http://www.odenki.org/api/Twitter/Callback"

class Twitter2(JsonRpcDispatcher):
    
    def GET(self, jrequest, jresponse):
        assert isinstance(jrequest, JsonRpcRequest)
        assert isinstance(jresponse, JsonRpcResponse)
        jresponse.setId()
        twitter_user = None
        odenki_user = None
        try:
            odenki_user = OdenkiUser.loadFromSession()
        except EntityNotFound: pass

        if odenki_user:
            try:
                twitter_user = TwitterUser.getByOdenkiId(odenki_user.odenkiId)
            except EntityNotFound: pass
        jresponse.setResult({"OdenkiUser": odenki_user, "TwitterUser":twitter_user})
        
    def deleteTwitterUser(self, jrequest, jresponse):
        assert isinstance(jrequest, JsonRpcRequest)
        assert isinstance(jresponse, JsonRpcResponse)
        jresponse.setId()
        odenki_user = OdenkiUser.loadFromSession()
        assert isinstance(odenki_user, OdenkiUser)
        twitter_user = TwitterUser.getByOdenkiId(odenki_user.odenkiId)
        assert isinstance(twitter_user, TwitterUser)
        twitter_user.key.delete()
        jresponse.setResultValue("OdenkiUser", odenki_user)
        
    def showAllTwitterUsers(self, jrequest, jresponse):
        assert isinstance(jrequest, JsonRpcRequest)
        assert isinstance(jresponse, JsonRpcResponse)
        assert jrequest.fromAdminHost
        jresponse.setId()
        query = TwitterUser.query()
        twitter_users=[]
        for twitter_user in query:
            twitter_users.append(twitter_user)
        jresponse.setResult(twitter_users)
        
    def deleteAllTwitterUsers(self, jrequest, jresponse):
        assert isinstance(jrequest, JsonRpcRequest)
        assert isinstance(jresponse, JsonRpcResponse)
        assert jrequest.fromAdminHost
        jresponse.setId()
        query = TwitterUser.query()
        for twitter_user_key in query.fetch(keys_only=True):
            assert isinstance(twitter_user_key, ndb.Key)
            twitter_user_key.delete_async()
        
REQUEST_TOKEN_SESSION_KEY = ";klsuioayggahihiaoheiajfioea"
REQUEST_TOKEN_SECRET_SESSION_KEY = "gscfgnhbfvcfscgdfgiubH"

class RedirectToAuthorizeUrl(JsonRpcDispatcher):
    
    def GET(self, jrequest, jresponse):
        assert isinstance(jrequest, JsonRpcRequest)
        assert isinstance(jresponse, JsonRpcResponse)
        jresponse.setId()
        consumer = oauth2.Consumer(TWITTER_CONSUMER_KEY, TWITTER_CONSUMER_SECRET)
        client = oauth2.Client(consumer)
        resp, content = client.request(REQUET_TOKEN_URL)
        if resp['status'] != '200':
            raise OAuthError({"consumer_key": TWITTER_CONSUMER_KEY, "request token url" :REQUET_TOKEN_URL})
        request_token_dict = dict(parse_qsl(content))
        try:
            request_token = request_token_dict["oauth_token"]
            request_token_secret = request_token_dict["oauth_token_secret"]
        except KeyError:
            raise OAuthError("RedirectToAuthorizeUrl failed to obtain request token.")
        authorize_url_param = urlencode([("oauth_token", request_token)])
        authorize_url = AUTHORIZE_URL + "?" + authorize_url_param
        jresponse.setResultValue("authorize_url_param", authorize_url_param)
        jresponse.setResultValue("authorize_url", authorize_url)
        jresponse.setResultValue("request_token", request_token)
        jresponse.setResultValue("request_token_secret", request_token_secret)
        jresponse.setResultValue("request_token_dict", request_token_dict)
        session = gaesessions.get_current_session()
        session[REQUEST_TOKEN_SESSION_KEY] = request_token 
        session[REQUEST_TOKEN_SECRET_SESSION_KEY] = request_token_secret

        jresponse.setRedirectTarget(authorize_url)
        
class OAuthCallback(JsonRpcDispatcher):
    
    def GET(self, jrequest, jresponse):
        assert isinstance(jrequest, JsonRpcRequest)
        assert isinstance(jresponse, JsonRpcResponse)
        jresponse.setId()
        jresponse.setRedirectTarget("/html/auth/failed.html")
        try:
            oauth_token = jrequest.getValue("oauth_token")[0]
            oauth_verifier = jrequest.getValue("oauth_verifier")[0]
        except:
            raise OAuthError("OAuthCallback was called with neither oauth_token nor oauth_verifier.")
        
        session = gaesessions.get_current_session()
        try:
            request_token = session[REQUEST_TOKEN_SESSION_KEY]
            request_token_secret = session[REQUEST_TOKEN_SECRET_SESSION_KEY]
        except KeyError:
            raise OAuthError("Request token have not been obtained.")
        
        if oauth_token != request_token:
            raise OAuthError("OAuthCallback gets token which is not identical to retaining request token.")

        token = oauth2.Token(request_token, request_token_secret)
        token.set_verifier(oauth_verifier)
        consumer = oauth2.Consumer(TWITTER_CONSUMER_KEY, TWITTER_CONSUMER_SECRET)
        client = oauth2.Client(consumer, token)
        resp, content = client.request(ACCESS_TOKEN_URL, "POST")
        access_token_dict = dict(parse_qsl(content))
        try:
            access_token = access_token_dict["oauth_token"]
            access_token_secret = access_token_dict["oauth_token_secret"]
            user_id = access_token_dict["user_id"]
            screen_name = access_token_dict["screen_name"]
        except KeyError:
            raise OAuthError({"request_token": request_token,
                              "ACCESS_TOKEN_URL": ACCESS_TOKEN_URL
                              },
                             message="OAuthCallback failed to exchange verified request token to access token.")
    
        # prepare TwittrUser
        try: 
            twitter_user = TwitterUser.getByTwitterId(int(user_id))
            twitter_user.setAccessToken(access_token, access_token_secret)
            twitter_user.screenName = unicode(screen_name)
            twitter_user.verifyCredentials11()
            twitter_user.put_async()
        except EntityNotFound:
            twitter_user = TwitterUser.create(int(user_id))
            twitter_user.setAccessToken(access_token, access_token_secret)
            twitter_user.screenName = unicode(screen_name)
            twitter_user.verifyCredentials11()
            twitter_user.put()
        assert isinstance(twitter_user, TwitterUser)
        
        # prepare OdenkiUser
        try:
            odenki_user = OdenkiUser.loadFromSession()
        except EntityNotFound: 
            odenki_user = None
        
        # reconcile TwitterUser and OdenkiUser
        if odenki_user is None:
            if twitter_user.odenkiId is None:
                odenki_user = OdenkiUser.createNew()
                assert isinstance(odenki_user, OdenkiUser)
                odenki_user.saveToSession()
                twitter_user.setOdenkiId(odenki_user.odenkiId)
                twitter_user.put_async()
            else:
                odenki_user = OdenkiUser.getByOdenkiId(twitter_user.odenkiId)
                odenki_user.saveToSession()
        else:
            if twitter_user.odenkiId is None:
                odenki_user.saveToSession()
                twitter_user.setOdenkiId(odenki_user.odenkiId)
                twitter_user.put_async()
            else:
                if twitter_user.odenkiId != odenki_user.odenkiId:
                    raise InconsistentAuthentiation({twitter_user.__class__.__name__: twitter_user,
                                                     odenki_user.__class__.__name__:odenki_user})
                odenki_user.saveToSession()
        
        jresponse.setResultValue("OdenkiUser", odenki_user)
        jresponse.setResultValue("TwitterUser", twitter_user)
        jresponse.setRedirectTarget("/html/auth/succeeded.html")
        
if __name__ == "__main__":
    mapping = []
    mapping.append(("/api/auth/Twitter/RedirectToAuthorizeUrl", RedirectToAuthorizeUrl))
    mapping.append(("/api/auth/Twitter/OAuthCallback", OAuthCallback))
    mapping.append(("/api/auth/Twitter", Twitter2))
    from lib.gae import run_wsgi_app
    run_wsgi_app(mapping)
