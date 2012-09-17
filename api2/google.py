from __future__ import unicode_literals
from logging import debug
from gaesessions import get_current_session, Session
from lib.JsonRpc import *
from lib.GoogleAuthState import GoogleAuthSession
from gdata.gauth import OAuthHmacToken, ACCESS_TOKEN, AUTHORIZED_REQUEST_TOKEN, REQUEST_TOKEN

from google.appengine.api.users import User
#from google.appengine.api import users
#from gdata.docs.data import ResourceFeed, Resource
from credentials import GOOGLE_OAUTH_CONSUMER_KEY, GOOGLE_OAUTH_CONSUMER_SECRET
from gdata.gauth import AeSave, AeLoad, AuthorizeRequestToken, AeDelete
#from gdata.client import Unauthorized
from gdata.docs.client import DocsClient
#from google.appengine.ext.db import Model, StringProperty, IntegerProperty
from lib.gae import JsonRpcDispatcher, JsonRpcError, JsonRpcRequest, JsonRpcResponse 

SCOPE_CALENDER = 'https://www.google.com/calendar/feeds/'
SCOPE_DOCS_LIST = 'https://docs.google.com/feeds/'
SCOPE_SPREADSHEET = 'https://spreadsheets.google.com/feeds/'

GOOGLE_OAUTH_SCOPES = [SCOPE_DOCS_LIST, SCOPE_SPREADSHEET]


#def getDocsClient(self):
#    client = DocsClient(source='odenkiapi')
#    access_token = self.loadAccessToken()
#    if access_token is not None: 
#        client.auth_token = access_token
#    return client

#def getSpreadsheetsClient(self):
#    client = SpreadsheetsClient(source='odenkiapi')
#    access_token = self.loadAccessToken()
#    if access_token is not None: 
#        assert isinstance(access_token, OAuthHmacToken)
#        OAuthHmacToken
#        client.auth_token = access_token
#    return client

#def getResources(self):
#    client = self.getDocsClient()
#    assert isinstance(client, DocsClient)
#    resource_feed = client.get_resources(show_root=True)
#    return resource_feed

class _GoogleRequestHandler(JsonRpcDispatcher):
    
    def revoke(self, jrequest, jresponse):
        assert isinstance(jrequest, JsonRpcRequest)
        assert isinstance(jresponse, JsonRpcResponse)
        jresponse.setResultValue("gaesession", get_current_session())
        googleAuthSession = GoogleAuthSession()
        googleAuthSession.revoke()
        jresponse.setResultValue("googleAuthSession", googleAuthSession)

    def GET(self, jrequest, jresponse):
        assert isinstance(jrequest, JsonRpcRequest)
        assert isinstance(jresponse, JsonRpcResponse)
        jresponse.setId()
        assert jresponse.getId()
        debug("GET called with id=%s" % jresponse.getId())
        jresponse.setResultValue("gaesession", get_current_session())
        #odenkiSession = OdenkiSession()
        #jresponse.setResultValue("odenkiSession", odenkiSession)
        googleAuthSession = GoogleAuthSession()
        debug("googleAuthSession has keys %s" %googleAuthSession.keys())
        jresponse.setResultValue("googleAuthSession", googleAuthSession)
        
        if googleAuthSession.getAccessToken():
            debug("access token %s already exists" % googleAuthSession.getAccessToken())
            debug("googleAuthSesson has keys %s" % googleAuthSession.keys())
            return
        
        if googleAuthSession.getNonAuthorizedRequestToken():
            assert googleAuthSession.getNonAuthorizedRequestToken().auth_state == REQUEST_TOKEN
            assert isinstance(googleAuthSession.getNonAuthorizedRequestToken(), OAuthHmacToken)
            debug("Extracting authorized request token from callback URL = " + self.request.url)
            authorized_request_token = AuthorizeRequestToken(googleAuthSession.getNonAuthorizedRequestToken(),
                                                             self.request.url)
            if authorized_request_token.token is None:
                googleAuthSession.revoke()
                assert not googleAuthSession._getToken()
                error_message = "Can't extract authorized request token from the URL %s" % self.request.url
                debug(error_message)
                assert jresponse.getId()
                jresponse.setError(JsonRpcError.SERVER_ERROR_RESERVED_MIN, error_message)
                return
            assert authorized_request_token.token
            assert authorized_request_token.auth_state == AUTHORIZED_REQUEST_TOKEN
            googleAuthSession.setAuthorizedRequestToken(authorized_request_token)
            debug("%s, %s" % (googleAuthSession.getAuthorizedRequestToken().token, authorized_request_token.token))
            assert googleAuthSession.getAuthorizedRequestToken().token == authorized_request_token.token

        if googleAuthSession.getAuthorizedRequestToken():
            assert isinstance(googleAuthSession.getAuthorizedRequestToken(), OAuthHmacToken)
            assert googleAuthSession.getAuthorizedRequestToken().auth_state == AUTHORIZED_REQUEST_TOKEN
            docs_client = DocsClient()
            try:
                access_token = docs_client.GetAccessToken(googleAuthSession.getAuthorizedRequestToken())
            except Exception, e:
                error_message = "failed to exchange authorized request token to access token, %s" % e
                debug(error_message)
                googleAuthSession.revoke()
                jresponse.setError(JsonRpcError.SERVER_ERROR_RESERVED_MIN, error_message)
                return
            assert isinstance(access_token, OAuthHmacToken)
            assert access_token.auth_state == ACCESS_TOKEN
            googleAuthSession.setAccessToken(access_token)
            assert googleAuthSession.getAccessToken().token is access_token.token
            debug("access token = %s" % googleAuthSession.getAccessToken)
            debug("after exchanging authorized request token with access token, googleAuthSession has keys %s" % googleAuthSession.keys())
            return

#        request_token = AeLoad(REQUEST_TOKEN_KEY)
#        if request_token is not None:
#            rpc.addLog("Request token was loaded by AeLoad.")
#            rpc.setResultValule("requestToken", request_token.token)
#            rpc.setResultValule("requestTokenSecret", request_token.token_secret)
#            rpc.setResultValule("requestTokenStatus", request_token.auth_state)
#            rpc.setResultValule("sid", odenki_session.getSid())
#            assert request_token.auth_state == REQUEST_TOKEN
#            assert isinstance(request_token, OAuthHmacToken)
#            authorized_request_token = AuthorizeRequestToken(request_token, self.request.url)
#            assert isinstance(authorized_request_token, OAuthHmacToken)
#            assert authorized_request_token.auth_state == AUTHORIZED_REQUEST_TOKEN
#            AeSave(authorized_request_token, REQUEST_TOKEN_KEY)
#            debug("Authorized request token was saved.")
#            docs_client = DocsClient()
#            try:
#                access_token = docs_client.GetAccessToken(authorized_request_token)
#                assert isinstance(access_token, OAuthHmacToken)
#                assert access_token.auth_state == ACCESS_TOKEN
#                debug("access token = " + access_token.token + ", secret = " + access_token.token_secret)
#                self.googleUser.setAccessToken(access_token)
#                assert isinstance(self.googleUser.getAccessToken(), OAuthHmacToken)
#                assert self.googleUser.getAccessToken().auth_state == ACCESS_TOKEN
#                #self.response.set_status(200)
#                #self.response.headers["Content-Type"] = "text/plain; charset=ascii"
#                rpc.addLog("Access token was saved..")
#                return
#            except Exception, e:
#                #self.response.set_status(500)
#                #self.response.headers["Content-Type"] = "text/plain; charset=ascii"
#                self.googleUser.deleteAccessToken()
#                AeDelete(REQUEST_TOKEN_KEY)
#                rpc.addLog("Couldn't exchange request token to access token. Request token was deleted.")
#                #rpc.setResultValule("message", "Request token was deleted.")
#                return
        
        debug("obtaining non-authorized request token")
        assert not googleAuthSession.getAuthorizedRequestToken()
        assert not googleAuthSession.getNonAuthorizedRequestToken()
        docs_client = DocsClient()
        non_authorized_request_token = docs_client.GetOAuthToken(
            GOOGLE_OAUTH_SCOPES,
            'http://%s/api/google' % self.request.host,
            GOOGLE_OAUTH_CONSUMER_KEY,
            consumer_secret=GOOGLE_OAUTH_CONSUMER_SECRET)
        assert isinstance(non_authorized_request_token, OAuthHmacToken)
        googleAuthSession.setNonAuthorizedRequestToken(non_authorized_request_token)
        assert googleAuthSession.getNonAuthorizedRequestToken().token == non_authorized_request_token.token
        assert isinstance(non_authorized_request_token, OAuthHmacToken)
        authorization_url = non_authorized_request_token.generate_authorization_url() #google_apps_domain=None
        assert isinstance(unicode(authorization_url), unicode)
        googleAuthSession.setAuthorizationUrl(unicode(authorization_url))
        #jresponse.setRedirectTarget(str(authorization_url))
        #assert jresponse.getRedirectTarget() == str(authorization_url)
        #debug("target = %s" % jresponse.getRedirectTarget())
        # prompting a page for user to authorize request.
        #debug("after setting redirection, googleAuthSession has keys %s" % googleAuthSession.keys())
        
        
if __name__ == "__main__":
    mapping = []
    mapping.append(("/api/google", _GoogleRequestHandler))
    from lib.gae import WSGIApplication
    application = WSGIApplication(mapping)
    from lib.gae import run_wsgi_app
    run_wsgi_app(application)
