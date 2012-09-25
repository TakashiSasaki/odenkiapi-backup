from __future__ import unicode_literals, print_function
from lib.gae.JsonRpcDispatcher import JsonRpcDispatcher
from lib.json.JsonRpcRequest import JsonRpcRequest
from lib.json.JsonRpcResponse import JsonRpcResponse
from credentials import TWITTER_CONSUMER_KEY, TWITTER_CONSUMER_SECRET
from model.TwitterUser import TwitterUser
from lib.json.JsonRpcError import EntityNotFound, MixedAuthentication, \
    OAuthError
import httplib2
import oauth2
from urlparse import parse_qsl
from urllib import urlencode
import gaesessions

"""Twitter OAuth consumer secret and consumer key for odenkiapi
can be obtained at https://dev.twitter.com/apps/1919034/show """

REQUET_TOKEN_URL = "https://api.twitter.com/oauth/request_token"
AUTHORIZE_URL = "https://api.twitter.com/oauth/authorize"
ACCESS_TOKEN_URL = "https://api.twitter.com/oauth/access_token"
CALLBACK_URL = "http://odenkiapi.appspot.com/api/Twitter/Callback"

class Twitter2(JsonRpcDispatcher):
    
    def GET(self, jrequest, jresponse):
        assert isinstance(jrequest, JsonRpcRequest)
        assert isinstance(jresponse, JsonRpcResponse)
        jresponse.setId()
        twitter_user = TwitterUser.loadFromSession()
        assert isinstance(twitter_user, TwitterUser)
        jresponse.setResultValue("twitterId", twitter_user.twitterId)
        jresponse.setResultValue("screenName", twitter_user.screenName)
        jresponse.setResultValue("odenkiId", twitter_user.odenkiId)
        jresponse.setResultValue("name", twitter_user.name)
        jresponse.setResultValue("locatioin", twitter_user.location)
        jresponse.setResultValue("profile_image_url", twitter_user.profile_image_url)
        jresponse.setResultValue("profile_image_url_https", twitter_user.profile_image_url_https)
        jresponse.setResultValue("description", twitter_user.description)
        jresponse.setResultValue("time_zone", twitter_user.time_zone)
        jresponse.setResultValue("url", twitter_user.url)
        jresponse.setResultValue("utc_offset", twitter_user.utc_offset)
        
    def deleteAll(self, jrequest, jresponse):
        assert isinstance(jrequest, JsonRpcRequest)
        assert isinstance(jresponse, JsonRpcResponse)
        jresponse.setId()
        TwitterUser.deleteAll()


        
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
        jresponse.setRedirectTarget("/html/auth/index.html")
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
            raise OAuthError("OAuthCallback failed to exchange verified request token to access token.")
        jresponse.setResultValue("access_token", access_token)
        jresponse.setResultValue("access_token_secret", access_token_secret)
        jresponse.setResultValue("uer_id", user_id)
        jresponse.setResultValue("screen_name", screen_name)
        jresponse.setResultValue("request_token", request_token)
        jresponse.setResultValue("request_token_secret", request_token_secret)
        jresponse.setResultValue("request_token_verified", oauth_token)
        jresponse.setResultValue("oauth_verifier", oauth_verifier)
        
        callback_twitter_user = TwitterUser()
        callback_twitter_user.setAccessToken(access_token, access_token_secret)
        callback_twitter_user.verifyCredentials11()
        callback_twitter_user.saveToSession()

        from lib.Session import fillUser
        fillUser()
        
        try:
            twitter_user = TwitterUser.loadFromSession()
            assert isinstance(twitter_user, TwitterUser)
            twitter_user.overrideBy(callback_twitter_user)
            twitter_user.put()
            twitter_user.saveToSession()
        except EntityNotFound: pass
        
        try:
            twitter_user = TwitterUser.getByTwitterId(callback_twitter_user.twitterId)
            assert isinstance(twitter_user, TwitterUser)
            twitter_user.overrideBy(callback_twitter_user)
            twitter_user.put()
            twitter_user.saveToSession()
        except EntityNotFound:
            callback_twitter_user.put()
            callback_twitter_user.saveToSession()
        fillUser()
        
if __name__ == "__main__":
    mapping = []
    mapping.append(("/api/Twitter2/RedirectToAuthorizeUrl", RedirectToAuthorizeUrl))
    mapping.append(("/api/Twitter2/OAuthCallback", OAuthCallback))
    mapping.append(("/api/Twitter2", Twitter2))
    from lib.gae import run_wsgi_app
    run_wsgi_app(mapping)
